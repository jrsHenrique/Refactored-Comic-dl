#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import logging
from comic_dl import globalFunctions
from comic_dl.sites.mangaDownloader import MangaDownloader

class MangaHere(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)

    def name_cleaner(self, url):
        """
        Implements name cleaning for MangaHere.
        """
        # Example cleaning logic
        return "Cleaned Comic Name"

    def single_chapter(self, comic_url):
        """
        Implements downloading a single chapter for MangaHere.
        """
        try:
            chapter_number = re.search(r"c(\d+\.\d+)", str(comic_url)).group(1)
        except:
            chapter_number = re.search(r"c(\d+)", str(comic_url)).group(1)

        source, cookies_main = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_url)
        last_page_number = str(re.search(r'total_pages\ \=\ (.*?) \;', str(source)).group(1)).strip()

        file_directory = globalFunctions.GlobalFunctions().create_file_directory(chapter_number, self.comic_name)
        directory_path = os.path.realpath(os.path.join(self.download_directory, file_directory))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        links = []
        file_names = []
        for chapCount in range(1, int(last_page_number) + 1):
            chapter_url = str(comic_url) + '/%s.html' % chapCount
            logging.debug("Chapter Url : %s" % chapter_url)

            source_new, cookies_new = globalFunctions.GlobalFunctions().page_downloader(manga_url=chapter_url,
                                                                                        cookies=cookies_main)

            image_link_finder = source_new.findAll('section', {'class': 'read_img'})

            for link in image_link_finder:
                x = link.findAll('img')
                for a in x:
                    image_link = a['src']

                    if image_link in ['http://www.mangahere.cc/media/images/loading.gif']:
                        pass
                    else:
                        logging.debug("Image Link : %s" % image_link)
                        file_name = str(globalFunctions.GlobalFunctions().prepend_zeroes(chapCount, len(x))) + ".jpg"
                        file_names.append(file_name)
                        links.append(image_link)

        globalFunctions.GlobalFunctions().multithread_download(chapter_number, self.comic_name, comic_url, directory_path,
                                                               file_names, links, self.logging)

        globalFunctions.GlobalFunctions().conversion(directory_path, self.conversion, self.keep_files, self.comic_name,
                                                     chapter_number)

        return 0

    def full_series(self):
        """
        Implements downloading a series of comics for MangaHere.
        """
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=self.manga_url)

        all_links = re.findall(r"class=\"color_0077\" href=\"(.*?)\"", str(source))

        chapter_links = []

        for link in all_links:
            if 'mangahere.cc/manga/' in link:
                chapter_links.append(link)
            else:
                pass

        logging.debug("All Links : %s" % all_links)

        if self.chapter_range != "All":
            starting = int(str(self.chapter_range).split("-")[0]) - 1

            if str(self.chapter_range).split("-")[1].isdigit():
                ending = int(str(self.chapter_range).split("-")[1])
            else:
                ending = len(chapter_links)

            indexes = [x for x in range(starting, ending)]

            chapter_links = [chapter_links[x] for x in indexes][::-1]
        else:
            chapter_links = chapter_links

        if self.print_index:
            idx = chapter_links.__len__()
            for chap_link in chapter_links:
                print(str(idx) + ": " + str(chap_link))
                idx = idx - 1
            return

        if str(self.sorting).lower() in ['new', 'desc', 'descending', 'latest']:
            for chap_link in chapter_links:
                try:
                    self.single_chapter(comic_url=str(chap_link))
                except Exception as ex:
                    logging.error("Error downloading : %s" % chap_link)
                    break
                
                if self.chapter_range != "All" and (self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                    globalFunctions.GlobalFunctions().addOne(self.manga_url)
                    
        elif str(self.sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            for chap_link in chapter_links[::-1]:
                try:
                    self.single_chapter(comic_url=str(chap_link))
                except Exception as ex:
                    logging.error("Error downloading : %s" % chap_link)
                    break
                
                if self.chapter_range != "All" and (self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                    globalFunctions.GlobalFunctions().addOne(self.manga_url)

        return 0

    def user_login(self):
        """
        Placeholder for user login implementation if needed.
        """
        # Implement user login logic here if required
        pass
