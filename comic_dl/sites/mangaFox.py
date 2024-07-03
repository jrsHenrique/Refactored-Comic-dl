#!/usr/bin/env python
# -*- coding: utf-8 -*-

from comic_dl import globalFunctions
import re
import os
import logging
import jsbeautifier
from comic_dl.sites.mangaDownloader import MangaDownloader


class MangaFox(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)

        url_split = str(manga_url).split("/")
        self.print_index = kwargs.get("print_index")

        if len(url_split) == 5:
            self.full_series()
        else:
            self.single_chapter(manga_url)

    def name_cleaner(self, url):
        initial_name = str(url).split("/")[4].strip()
        safe_name = re.sub(r"[0-9][a-z][A-Z]\ ", "", str(initial_name))
        manga_name = str(safe_name.title()).replace("_", " ")

        return manga_name

    def single_chapter(self, comic_url):
        comic_name = self.comic_name
        download_directory = self.download_directory
        conversion = self.conversion
        keep_files = self.keep_files

        source, cookies_main = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_url)
        url_split = str(comic_url).split('/')
        current_chapter_volume = url_split[-3]
        chapter_number = url_split[-2]
        series_code = url_split[-4]
        chapter_id = int(str(re.search(r'chapterid\s?=\s?(.*?);', str(source)).group(1)).strip())
        current_page_number = int(str(re.search(r'imagepage\s?=\s?(.*?);', str(source)).group(1)).strip())
        last_page_number = int(str(re.search(r'imagecount\s?=\s?(.*?);', str(source)).group(1)).strip())

        file_directory = globalFunctions.GlobalFunctions().create_file_directory(chapter_number, comic_name)
        directory_path = os.path.realpath(str(download_directory) + "/" + str(file_directory))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        links = {}
        appended_headers = {
            'referer': comic_url
        }
        for file_name in range(current_page_number, last_page_number + 1):
            script_url = "https://fanfox.net/manga/{0}/{1}/{2}/chapterfun.ashx?cid={3}&page={4}&key=".format(series_code,
                                                                                                        current_chapter_volume,
                                                                                                        chapter_number,
                                                                                                        chapter_id, file_name)
            script_source, cookies_main = globalFunctions.GlobalFunctions().page_downloader(manga_url=script_url,
                                                                                            cookies=cookies_main,
                                                                                            append_headers=appended_headers)
            if not script_source:
                return False  # Couldn't fetch script to find CDN network name and image file info
            beautified_script = jsbeautifier.beautify(script_source.text)
            pix_url = str(re.search(r'pix\s+=\s+"(.*?)";', str(beautified_script)).group(1).strip())
            p_values = re.search(r'pvalue = \[(.*?)\];', str(beautified_script)).group(1).strip().replace('"', '').split(',')
            if len(p_values) > 0:
                file_name_custom = str(globalFunctions.GlobalFunctions().prepend_zeroes(file_name, last_page_number + 1)) + ".jpg"
                image_url = "https:{0}{1}".format(pix_url, p_values[0].strip())
                links[file_name_custom] = image_url

        globalFunctions.GlobalFunctions().multithread_download(chapter_number, comic_name, comic_url, directory_path,
                                                            list(links.keys()), list(links.values()), self.logging, append_headers=appended_headers)

        globalFunctions.GlobalFunctions().conversion(directory_path, conversion, keep_files, comic_name,
                                                    chapter_number)

        return 0

    def full_series(self):
        comic_url = self.manga_url
        comic_name = self.comic_name
        sorting = self.sorting
        download_directory = self.download_directory
        chapter_range = self.chapter_range
        conversion = self.conversion
        keep_files = self.keep_files

        rss_url = str(comic_url).replace("/manga/", "/rss/") + ".xml"
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=rss_url)

        all_links_temp = re.findall(r"/manga/(.*?).html", str(source))
        all_links = ["https://fanfox.net/manga/{0}.html".format(link) for link in all_links_temp]

        logging.debug("All Links : %s" % all_links)

        if chapter_range != "All":
            starting = int(str(chapter_range).split("-")[0]) - 1
            ending = int(str(chapter_range).split("-")[1]) if str(chapter_range).split("-")[1].isdigit() else len(all_links)
            indexes = [x for x in range(starting, ending)]
            all_links = [all_links[len(all_links) - 1 - x] for x in indexes][::-1]

        if self.print_index:
            idx = len(all_links)
            for chap_link in all_links:
                print(str(idx) + ": " + chap_link)
                idx -= 1
            return


        if sorting.lower() in ['new', 'desc', 'descending', 'latest']:
            chapter_list = all_links
        elif sorting.lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            chapter_list = all_links[::-1]


        for chap_link in chapter_list:
            try:
                self.single_chapter(comic_url=chap_link)
            except Exception as ex:
                logging.error("Error downloading : %s" % chap_link)
                logging.error(ex)
                break  

        return 0
    
    def user_login(self):
        pass
