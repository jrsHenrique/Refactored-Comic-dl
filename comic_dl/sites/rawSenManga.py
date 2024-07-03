#!/usr/bin/env python
# -*- coding: utf-8 -*-

from comic_dl import globalFunctions
import os
import logging
import re
import json
from comic_dl.sites.mangaDownloader import MangaDownloader


class RawSenaManga(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)

    def download_single_chapter(self):
        chapter_number = str(self.manga_url).split("/")[4].strip()

        source, cookies_main = globalFunctions.GlobalFunctions().page_downloader(manga_url=self.manga_url)

        image_url = "http://raw.senmanga.com/viewer/" + str(self.comic_name).replace(" ", "-") + "/" + str(
            chapter_number) + "/"

        page_referer = "http://raw.senmanga.com/" + str(self.comic_name).replace(" ", "-") + "/" + str(
            chapter_number) + "/"

        last_page_number = int(str(re.search(r"</select> of (\d+) <a", str(source)).group(1)).strip())

        file_directory = globalFunctions.GlobalFunctions().create_file_directory(chapter_number, self.comic_name)
        directory_path = os.path.realpath(str(self.download_directory) + "/" + str(file_directory))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        links = []
        file_names = []
        for x in range(0, last_page_number + 1):
            if x == 0:
                pass
            else:
                ddl_image = str(image_url) + str(x)
                referer = str(page_referer) + str(x - 1)
                logging.debug("Image Link : %s" % ddl_image)

                file_name = str(globalFunctions.GlobalFunctions().prepend_zeroes(x, last_page_number + 1)) + ".jpg"
                
                links.append(ddl_image)
                file_names.append(file_name)

        globalFunctions.GlobalFunctions().multithread_download(chapter_number, self.comic_name, self.manga_url,
                                                               directory_path, file_names, links, self.logging)

        globalFunctions.GlobalFunctions().conversion(directory_path, self.conversion, self.keep_files, self.comic_name,
                                                     chapter_number)

        return 0

    def download_full_series(self):
        series_name_raw = str(self.manga_url).split("/")[3].strip()
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=self.manga_url)

        link_regex = "<a href=\".*/" + str(series_name_raw) + "/(.*?)\""
        all_links = list(re.findall(link_regex, str(source)))
        logging.debug("All Links : %s" % all_links)

        if self.chapter_range != "All":
            starting = int(str(self.chapter_range).split("-")[0]) - 1

            if str(self.chapter_range).split("-")[1].isdigit():
                ending = int(str(self.chapter_range).split("-")[1])
            else:
                ending = len(all_links)

            indexes = [x for x in range(starting, ending)]
            all_links = [all_links[x] for x in indexes][::-1]
        else:
            all_links = all_links

        if self.print_index:
            link_regex = "<a href=\".*/" + str(series_name_raw) + "/.*>(.*)</a>"
            all_links = list(re.findall(link_regex, str(source)))
            idx = len(all_links)
            for link in all_links:
                print(str(idx) + ": " + link)
                idx = idx - 1
            return

        if str(self.sorting).lower() in ['new', 'desc', 'descending', 'latest']:
            for link in all_links:
                chap_link = "http://raw.senmanga.com/" + str(series_name_raw) + "/" + str(link).strip()
                try:
                    self.download_single_chapter(comic_url=chap_link, comic_name=self.comic_name,
                                                 download_directory=self.download_directory,
                                                 conversion=self.conversion, keep_files=self.keep_files)
                except Exception as ex:
                    logging.error("Error downloading : %s" % chap_link)
                    break

                if self.chapter_range != "All" and (
                        self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                    globalFunctions.GlobalFunctions().addOne(self.manga_url)

        elif str(self.sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            for link in all_links[::-1]:
                chap_link = "http://raw.senmanga.com/" + str(series_name_raw) + "/" + str(link).strip()
                try:
                    self.download_single_chapter(comic_url=chap_link, comic_name=self.comic_name,
                                                 download_directory=self.download_directory,
                                                 conversion=self.conversion, keep_files=self.keep_files)
                except Exception as ex:
                    logging.error("Error downloading : %s" % chap_link)
                    break

                if self.chapter_range != "All" and (
                        self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                    globalFunctions.GlobalFunctions().addOne(self.manga_url)

        return 0
