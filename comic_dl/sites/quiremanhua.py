#!/usr/bin/env python
# -*- coding: utf-8 -*-

from comic_dl import globalFunctions
import os
import logging
import json
from comic_dl.sites.mangaDownloader import MangaDownloader
import re



class QuireManhua(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)

    def download_single_chapter(self):
        comic_url = str(self.manga_url)
        chapter_info = kwargs.get("chapters_info", None)
        chapter_number = 0
        chapter_name = None

        if not chapter_info:
            print("Getting chapter info")
            chapter_source = self.get_chapter_list()
            for chapter in chapter_source['data']:
                if int(self.chapter_id) == int(chapter['chapterId']):
                    chapter_number = chapter['chapter_px']
                    chapter_name = chapter['chapterName']
                    break
        else:
            chapter_number = chapter_info['chapter_id']
            chapter_name = chapter_info['chapter_name']

        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_url,
                                                                            cookies=self.manual_cookie)

        if not self.comic_name:
            com_nm = source.find("a", {"class": "active"})
            if com_nm:
                self.comic_name = com_nm.text

        image_list_elems = source.find_all("img", {"class": "lazy show-menu chapter-img"})
        links = []
        file_names = []

        if len(image_list_elems) > 0:
            for _idx, elem in enumerate(image_list_elems):
                img_url = str(elem['src']).strip()
                links.append(img_url)
                img_extension = str(img_url).rsplit('.', 1)[-1]
                file_names.append('{0}.{1}'.format(_idx, img_extension))
        else:
            print("Locked content. Returning without downloading {0}".format(comic_url))
            return 1

        chapter_name_string = chapter_number if not chapter_name else "{0} - {1}".format(chapter_number, chapter_name)
        file_directory = globalFunctions.GlobalFunctions().create_file_directory(chapter_name_string, self.comic_name)

        directory_path = os.path.realpath(str(self.download_directory) + "/" + str(file_directory))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        globalFunctions.GlobalFunctions().multithread_download(chapter_name_string, self.comic_name, comic_url,
                                                               directory_path, file_names, links, self.logging)

        globalFunctions.GlobalFunctions().conversion(directory_path, self.conversion, self.keep_files,
                                                     self.comic_name, chapter_name_string)

        return 0

    def download_full_series(self):
        if self.book_id <= 0:
            print("Invalid book Id. Exiting")
            return 0

        source = self.get_chapter_list()
        all_links = []
        chapters_info = {}

        for chapter in source['data']:
            chapter_url = "https://www.qiremanhua.com/book/{0}/{1}".format(self.book_id, chapter['chapterId'])
            all_links.append(chapter_url)
            chapters_info[chapter['chapterId']] = {
                'chapter_id': chapter['chapter_px'],
                'chapter_name': chapter['chapterName']
            }

        if self.chapter_range != "All":
            starting = int(str(self.chapter_range).split("-")[0]) - 1

            if str(self.chapter_range).split("-")[1].isdigit():
                ending = int(str(self.chapter_range).split("-")[1])
            else:
                ending = len(all_links)

            indexes = [x for x in range(starting, ending)]
            all_links = [all_links[x] for x in indexes][::-1]

        if self.print_index:
            idx = 0
            for chap_link in all_links:
                idx = idx + 1
                print(str(idx) + ": " + chap_link)
            return

        if str(self.sorting).lower() in ['new', 'desc', 'descending', 'latest']:
            for chap_link in all_links:
                try:
                    chap_id = int(chap_link.rsplit('/', 1)[-1])
                    self.download_single_chapter(comic_url=chap_link, comic_name=self.comic_name,
                                                 download_directory=self.download_directory,
                                                 conversion=self.conversion, keep_files=self.keep_files,
                                                 chapters_info=chapters_info[chap_id])
                except Exception as ex:
                    logging.error("Error downloading : %s" % chap_link)
                    break

                if self.chapter_range != "All" and (
                        self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                    globalFunctions.GlobalFunctions().addOne(self.manga_url)

        elif str(self.sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            for chap_link in all_links[::-1]:
                try:
                    chap_id = int(chap_link.rsplit('/', 1)[-1])
                    self.download_single_chapter(comic_url=chap_link, comic_name=self.comic_name,
                                                 download_directory=self.download_directory,
                                                 conversion=self.conversion, keep_files=self.keep_files,
                                                 chapters_info=chapters_info.get(chap_id))
                except Exception as ex:
                    logging.error("Error downloading : %s" % chap_link)
                    break

                if self.chapter_range != "All" and (
                        self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                    globalFunctions.GlobalFunctions().addOne(self.manga_url)

        return 0

    def get_chapter_list(self):
        chapter_list_url = "https://www.qiremanhua.com/book/ajax_chapteres?bookId={0}".format(self.book_id)
        source, self.manual_cookie = globalFunctions.GlobalFunctions().page_downloader(manga_url=chapter_list_url,
                                                                                       cookies=self.manual_cookie)
        if source:
            source = json.loads(str(source))
        return source
