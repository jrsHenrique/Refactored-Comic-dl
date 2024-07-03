#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from comic_dl import globalFunctions
import os
import logging

from comic_dl.sites.mangaDownloader import MangaDownloader


class ComicExtra(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)

        if "/comic/" in manga_url:
            self.full_series()
        else:
            self.single_chapter(manga_url)

    def name_cleaner(self, url):
        return re.sub(r"[0-9][a-z][A-Z]\ ", "", url.split("/")[-1].replace("%20", " ").replace("-", " ").title())

    def user_login(self):
        pass

    def single_chapter(self, comic_url):
        comic_name = self.name_cleaner(comic_url)
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_url)
        img_list = []

        first_image_link_bs = source.find_all('div', {'class': 'chapter-main'})
        for single_node in first_image_link_bs:
            x = single_node.findAll('img')
            for a in x:
                img_list.append(str(a['src']).strip())

        chapter_number = comic_url.split("-")[-1].replace("/full", "")
        total_pages = len(img_list)

        file_directory = globalFunctions.GlobalFunctions().create_file_directory(chapter_number, comic_name)
        directory_path = os.path.realpath(self.download_directory + "/" + file_directory)

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        links = []
        file_names = []
        for current_chapter, chapter_link in enumerate(img_list):
            current_chapter += 1
            file_name = str(globalFunctions.GlobalFunctions().prepend_zeroes(current_chapter, total_pages)) + ".jpg"
            file_names.append(file_name)
            links.append(chapter_link)

        globalFunctions.GlobalFunctions().multithread_download(chapter_number, comic_name, comic_url, directory_path,
                                                               file_names, links, self.logging)
        globalFunctions.GlobalFunctions().conversion(directory_path, self.conversion, self.keep_files, comic_name,
                                                     chapter_number)

        return 0

    def full_series(self):
        comic_name = self.name_cleaner(self.manga_url)
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=self.manga_url)
        all_links = []
        chap_holder_div = source.find_all('tbody', {'id': 'list'})
        for single_node in chap_holder_div:
            x = single_node.findAll('a')
            for a in x:
                all_links.append(str(a['href']).strip())

        indexes = self.get_chapter_range_indices(self.chapter_range, len(all_links))
        chapters_to_download = [all_links[x] for x in indexes]

        if not chapters_to_download:
            print("Couldn't find the chapter list")
            return 1

        for chap_link in chapters_to_download:
            chap_link += "/full"
            self.single_chapter(chap_link)

    def get_chapter_range_indices(self, range_spec, total_chapters):
        if range_spec == "All":
            return range(total_chapters)
        start, end = map(int, range_spec.split("-"))
        return range(start - 1, end)  # assuming chapter_range is 1-based