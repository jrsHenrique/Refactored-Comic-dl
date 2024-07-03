#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import shutil
import sys
import json
import math
import threading
import logging
import glob
import img2pdf
import requests
import cloudscraper
from bs4 import BeautifulSoup
from tqdm import tqdm
from queue import Queue

def easy_slug(string, repl="-", directory=False):
    """
    Function to create slug-like strings from input strings.

    Args:
        string (str): Input string to slugify.
        repl (str): Replacement character for non-alphanumeric characters.
        directory (bool): Flag indicating if the string is a directory name.

    Returns:
        str: Slugified string.
    """
    if directory:
        return re.sub("^\.|\.+$", "", easy_slug(string, directory=False))
    else:
        return re.sub(r"[\\\\/:*?\"<>\|]|\ $", repl, string)

def merge_two_dicts(x, y):
    """
    Merge two dictionaries.

    Args:
        x (dict): First dictionary.
        y (dict): Second dictionary.

    Returns:
        dict: Merged dictionary.
    """
    z = x.copy()
    z.update(y)
    return z

class GlobalFunctions:
    """
    Class containing global utility functions.
    """
    @staticmethod
    def page_downloader(manga_url, scrapper_delay=5, **kwargs):
        """
        Download page source and cookies from a manga URL.

        Args:
            manga_url (str): URL of the manga page.
            scrapper_delay (int): Delay for cloudscraper.
            **kwargs: Additional arguments for headers, cookies.

        Returns:
            BeautifulSoup object, requests cookies: Parsed page source and connection cookies.
        """
        headers = kwargs.get("headers") or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate'
        }
        if kwargs.get('append_headers'):
            headers = merge_two_dicts(headers, dict(kwargs.get('append_headers')))

        sess = requests.session()
        sess = cloudscraper.create_scraper(sess, delay=scrapper_delay)

        connection = sess.get(manga_url, headers=headers, cookies=kwargs.get("cookies"))

        if connection.status_code != 200:
            raise Warning("Can't connect to website %s" % manga_url)

        page_source = BeautifulSoup(connection.text.encode("utf-8"), "html.parser")
        connection_cookies = sess.cookies

        return page_source, connection_cookies

    @staticmethod
    def downloader(image_and_name, referer, directory_path, **kwargs):
        """
        Download images.

        Args:
            image_and_name (tuple): Tuple containing image URL and file name.
            referer (str): Referer URL.
            directory_path (str): Directory path to save images.
            **kwargs: Additional arguments for headers, cookies, progress bar.

        Raises:
            Various exceptions on connection errors or HTTP errors.
        """
        logging.basicConfig(level=logging.DEBUG)
        pbar = kwargs.get("pbar")

        image_ddl = image_and_name[0]
        file_name = image_and_name[1]
        file_check_path = os.path.join(directory_path, file_name)

        logging.debug(f"File Check Path : {file_check_path}")
        logging.debug(f"Download File Name : {file_name}")

        if os.path.isfile(file_check_path):
            pbar.write('[Comic-dl] File Exist! Skipping : %s\n' % file_name)
            return

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': referer
        }
        if kwargs.get('append_headers'):
            headers = merge_two_dicts(headers, dict(kwargs.get('append_headers')))

        sess = requests.session()
        sess = cloudscraper.create_scraper(sess)
        try:
            r = sess.get(image_ddl, stream=True, headers=headers, cookies=kwargs.get("cookies"))
            r.raise_for_status()
            if r.status_code != 200:
                pbar.write("Could not download the image.")
                pbar.write("Link said : %s" % r.status_code)
                return
            else:
                with open(file_check_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()

                file_path = os.path.normpath(file_check_path)
                try:
                    shutil.move(file_path, directory_path)
                except Exception as file_moving_exception:
                    pbar.write(str(file_moving_exception))
                    os.remove(file_path)
                    raise file_moving_exception
        except requests.exceptions.RequestException as ex:
            pbar.write("Error occurred while downloading: %s" % file_name)
            pbar.write(str(ex))
            raise
        finally:
            pbar.update()

    @staticmethod
    def conversion(directory_path, conversion, keep_files, comic_name, chapter_number):
        """
        Convert downloaded images to PDF or CBZ format.

        Args:
            directory_path (str): Directory containing images.
            conversion (str): Desired conversion format ('pdf', 'cbz', etc.).
            keep_files (bool): Flag to indicate whether to keep original files.
            comic_name (str): Name of the comic.
            chapter_number (int): Chapter number.

        Raises:
            Various exceptions during file operations or conversion errors.
        """
        main_directory = directory_path.split(os.sep)
        main_directory.pop()
        converted_file_directory = os.path.join(os.sep.join(main_directory)) + os.sep

        try:
            if str(conversion).lower().strip() == 'pdf':
                im_files = [image_files for image_files in sorted(glob.glob(os.path.join(directory_path, "*.jpg")),
                                                                  key=lambda x: int(os.path.split(x)[1].split('.')[0]))]
                pdf_file_name = os.path.join(converted_file_directory, "{0} - Ch {1}.pdf".format(easy_slug(comic_name), chapter_number))
                if os.path.isfile(pdf_file_name):
                    print('[Comic-dl] PDF File Exist! Skipping : {0}\n'.format(pdf_file_name))
                    return
                else:
                    with open(pdf_file_name, "wb") as f:
                        f.write(img2pdf.convert(im_files))
                        print("Converted the file to PDF...")
                        return

            elif str(conversion).lower().strip() == 'cbz':
                cbz_file_name = os.path.join(converted_file_directory, "{0} - Ch {1}".format(easy_slug(comic_name), chapter_number))
                print("CBZ File : {0}".format(cbz_file_name))

                if os.path.isfile(cbz_file_name + ".cbz"):
                    print('[Comic-dl] CBZ File Exist! Skipping : {0}\n'.format(cbz_file_name))
                    return
                else:
                    shutil.make_archive(cbz_file_name, 'zip', directory_path)
                    os.rename(cbz_file_name + ".zip", cbz_file_name + ".cbz")
                    return

            elif str(conversion).lower().strip() == "none":
                return

            else:
                print("Unsupported conversion format: %s" % conversion)
                return

        except Exception as ex:
            print("Error occurred during conversion: %s" % str(ex))
            return

        finally:
            if str(keep_files).lower().strip() in ['no', 'false', 'delete']:
                try:
                    shutil.rmtree(path=directory_path, ignore_errors=True)
                    print("Deleted the files...")
                except Exception as DirectoryDeleteError:
                    print("Failed to delete the directory: %s" % str(DirectoryDeleteError))

    @staticmethod
    def add_one(comic_url):
        """
        Increment 'next' value in JSON configuration file for a given comic URL.

        Args:
            comic_url (str): URL of the comic.

        Raises:
            FileNotFoundError: If config.json file is not found.
            JSONDecodeError: If config.json is not a valid JSON file.
        """
        try:
            with open('config.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as ex:
            print("Error loading config.json: %s" % str(ex))
            return

        for elKey in data.get("comics", {}).keys():
            json_url = data["comics"][elKey]["url"]
            if json_url == comic_url or json_url == comic_url + "/":
                data["comics"][elKey]["next"] += 1

        try:
            with open('config.json', 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as ex:
            print("Error writing to config.json: %s" % str(ex))
            return

    @staticmethod
    def prepend_zeroes(current_chapter_value, total_images):
        """
        Add leading zeroes to current chapter value.

        Args:
            current_chapter_value (int): Current chapter number.
            total_images (int): Total number of images.

        Returns:
            str: Formatted chapter number with leading zeroes.
        """
        max_digits = int(math.log10(int(total_images))) + 1
        return str(current_chapter_value).zfill(max_digits)

    @staticmethod
    def multithread_download(chapter_number, comic_name, comic_url, directory_path, file_names, links, log_flag,
                             pool_size=4, **kwargs):
        """
        Download images using multiple threads.

        Args:
            chapter_number (int): Chapter number.
            comic_name (str): Name of the comic.
            comic_url (str): URL of the comic.
            directory_path (str): Directory path to save images.
            file_names (list): List of file names to download.
            links (list): List of image URLs.
            log_flag (bool): Flag for logging.
            pool_size (int): Number of threads.
            **kwargs: Additional arguments for headers, cookies, progress bar.
        """
        def worker():
            while True:
                try:
                    worker_item = in_queue.get()
                    GlobalFunctions.downloader(referer=comic_url, directory_path=directory_path, pbar=pbar, log_flag=log_flag,
                                               image_and_name=worker_item, **kwargs)
                    in_queue.task_done()
                except Queue.empty:
                    logging.info("Queue is empty.")
                    return
                except Exception as ex:
                    err_queue.put(ex)
                    in_queue.task_done()

        in_queue = Queue()
        err_queue = Queue()

        pbar = tqdm(links, leave=True, unit='image(s)', position=0)
        pbar.set_description('[Comic-dl] Downloading : %s [%s] ' % (comic_name, chapter_number))

        for i in range(pool_size):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()

        for item in zip(links, file_names):
            in_queue.put(item)

        in_queue.join()

        try:
            while not err_queue.empty():
                err = err_queue.get(block=False)
                pbar.set_description('[Comic-dl] Error : %s [%s] - %s ' % (comic_name, chapter_number, err))
                raise err
        except Queue.empty:
            pbar.set_description('[Comic-dl] Done : %s [%s] ' % (comic_name, chapter_number))
        finally:
            pbar.close()

    @staticmethod
    def create_file_directory(chapter_number, comic_name, dynamic_sub=None):
        """
        Create directory path for storing downloaded files.

        Args:
            chapter_number (int): Chapter number.
            comic_name (str): Name of the comic.
            dynamic_sub (str): Optional dynamic substring for directory name.

        Returns:
            str: File directory path.
        """
        comic = comic_name
        if dynamic_sub:
            comic = re.sub(rf'[^\w\-_. \[\]{dynamic_sub}]', '-', str(comic_name))
        else:
            comic = re.sub(r'[^\w\-_. \[\]]', '-', str(comic_name))
        chapter = re.sub(r'[^\w\-_. \[\]]', '-', str(chapter_number))
        file_directory = comic + os.sep + chapter + os.sep
        return file_directory