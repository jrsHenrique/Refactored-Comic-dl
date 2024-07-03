#!/usr/bin/env python
# -*- coding: utf-8 -*-

from comic_dl import globalFunctions
import re
import sys
import os
import logging
from comic_dl.sites.mangaDownloader import MangaDownloader


class FoolSlide(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)
        if "/reader/series/" in manga_url:
            self.full_series()
        elif "/reader/read/" in manga_url:
            self.single_chapter(manga_url)

    def name_cleaner(self, url):
        initial_name = str(url).split("/")[5].strip()
        safe_name = re.sub(r"[0-9][a-z][A-Z]\ ", "", str(initial_name))
        manga_name = str(safe_name.title()).replace("-", " ")
        return manga_name

    def single_chapter(self, chapter_url):
        chapter_number = str(chapter_url).split("/")[8].strip()
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=chapter_url)
        img_links = self.image_links(source)
        logging.debug("Img Links : %s" % img_links)

        file_directory = globalFunctions.GlobalFunctions().create_file_directory(chapter_number, self.comic_name)
        directory_path = os.path.realpath(str(self.download_directory) + "/" + str(file_directory))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        links = []
        file_names = []
        for current_chapter, image_link in enumerate(img_links):
            new_link = image_link.replace("\\", "")
            current_chapter += 1
            file_name = str(globalFunctions.GlobalFunctions().prepend_zeroes(current_chapter, len(img_links))) + ".jpg"
            file_names.append(file_name)
            links.append(new_link)

        globalFunctions.GlobalFunctions().multithread_download(chapter_number, self.comic_name, self.comic_name, directory_path,
                                                               file_names, links, self.logging)

        globalFunctions.GlobalFunctions().conversion(directory_path, self.conversion, self.keep_files, self.comic_name,
                                                     chapter_number)

        return 0

    def full_series(self):
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=self.manga_url)
        chapter_text = source.findAll('div', {'class': 'title'})
        all_links = []

        for link in chapter_text:
            x = link.findAll('a')
            for a in x:
                url = a['href']
                all_links.append(url)
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

        if str(self.sorting).lower() in ['new', 'desc', 'descending', 'latest']:
            for chap_link in all_links:
                try:
                    self.single_chapter(chap_link)
                except Exception as ex:
                    logging.error("Error downloading : %s" % chap_link)
                    break
                if self.chapter_range != "All" and (self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                    globalFunctions.GlobalFunctions().addOne(self.manga_url)
        elif str(self.sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            for chap_link in all_links[::-1]:
                try:
                    self.single_chapter(chap_link)
                except Exception as ex:
                    logging.error("Error downloading : %s" % chap_link)
                    break
                if self.chapter_range != "All" and self.chapter_range.split("-")[1] == "__EnD__":
                    globalFunctions.GlobalFunctions().addOne(self.manga_url)

        return 0

    def image_links(self, source_code):
        try:
            source_dict = re.search(r"\= \[(.*?)\]\;", str(source_code)).group(1)
            image_links = re.findall(r"\"url\"\:\"(.*?)\"", str(source_dict))
        except Exception as ImageLinksNotFound:
            print("Links : %s" % ImageLinksNotFound)
            sys.exit()
        return image_links
