#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from comic_dl import globalFunctions
import os
import logging
from comic_dl.sites.mangaDownloader import MangaDownloader


class Hqbr(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)
        self.comic_name = self.name_cleaner(manga_url)
        self.print_index = kwargs.get("print_index")

        if "/hqs/" in manga_url:
            self.single_chapter(manga_url)
        else:
            self.full_series()

    def name_cleaner(self, url):
        manga_name = re.sub(r"[0-9][a-z][A-Z]\ ", "", str(url).split("/")[4].split("?")[0].replace("%20", " ").title())
        return manga_name

    def single_chapter(self, comic_url):
        chapter_number = int(str(comic_url).split("/")[6].strip())
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_url)
        links_string = re.search(r'pages = \[(.*?)\]', str(source)).group(1)
        img_list = re.findall(r'\"(.*?)\"', str(links_string))

        file_directory = str(self.comic_name) + '/' + str(chapter_number) + "/"
        file_directory = file_directory.replace(":", "-")
        directory_path = os.path.realpath(str(self.download_directory) + "/" + str(file_directory))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        links = []
        file_names = []
        for page_count, image_link in enumerate(img_list):
            page_count += 1
            file_name = str(globalFunctions.GlobalFunctions().prepend_zeroes(page_count, len(img_list))) + ".jpg"
            file_names.append(file_name)
            links.append("https://hqbr.com.br" + str(image_link))

        globalFunctions.GlobalFunctions().multithread_download(chapter_number, self.comic_name, comic_url, directory_path,
                                                               file_names, links, self.logging)

        globalFunctions.GlobalFunctions().conversion(directory_path, self.conversion, self.keep_files, self.comic_name,
                                                     chapter_number)
        return 0

    def full_series(self):
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=self.manga_url)
        all_links = []
        chap_holder_div = source.find_all('table', {'class': 'table table-hover'})
        for single_node in chap_holder_div:
            x = single_node.findAll('a')
            for a in x:
                all_links.append("https://hqbr.com.br" + str(a['href']).strip())

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

        if not all_links:
            print("Couldn't find the chapter list")
            return 1

        if self.print_index:
            idx = len(all_links)
            for chap_link in all_links:
                print(str(idx) + ": " + chap_link)
                idx -= 1
            return

        if str(self.sorting).lower() in ['new', 'desc', 'descending', 'latest']:
            for chap_link in all_links:
                try:
                    self.single_chapter(chap_link)
                    if self.chapter_range != "All" and (self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                        globalFunctions.GlobalFunctions().addOne(self.manga_url)
                except Exception as ex:
                    logging.error("Error downloading: %s" % chap_link)
                    break

        elif str(self.sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            for chap_link in all_links[::-1]:
                try:
                    self.single_chapter(chap_link)
                    if self.chapter_range != "All" and (self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                        globalFunctions.GlobalFunctions().addOne(self.manga_url)
                except Exception as ex:
                    logging.error("Error downloading: %s" % chap_link)
                    break

        return 0
