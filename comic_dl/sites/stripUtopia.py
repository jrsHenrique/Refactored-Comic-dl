#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
from comic_dl import globalFunctions
from comic_dl.sites.mangaDownloader import MangaDownloader

class StripUtopia(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)
        self.logging = kwargs.get("log_flag")
        self.sorting = kwargs.get("sorting_order")
        self.print_index = kwargs.get("print_index")
        self.comic_name = None

        page_source, cookies_main = self.page_downloader(manga_url=manga_url)
        self.comic_name = self.name_cleaner(page_source, manga_url)

        if "/p/" in str(manga_url):
            self.full_series(source=page_source, comic_url=manga_url, comic_name=self.comic_name,
                             sorting=self.sorting, download_directory=download_directory,
                             chapter_range=chapter_range, conversion=self.conversion, keep_files=self.keep_files)
        else:
            self.single_chapter(page_source, manga_url, self.comic_name, download_directory,
                                self.conversion, self.keep_files)

    def name_cleaner(self, source, url):
        initial_name = re.search(r"<title>\n(.*?)\n</title>", str(source)).group(1)
        safe_name = re.sub(r"[0-9][a-z][A-Z]\ ", "", str(initial_name))
        name_breaker = safe_name.split("-")[-1]
        manga_name = str(name_breaker.title()).replace("_", " ").replace("Strip-Utopija", "").replace("STRIP-UTOPIJA",
                                                                                                      "").replace(
            "UTOPIJA", "").replace("Utopija", "").replace(":", "").strip()
        return manga_name

    def single_chapter(self, source, comic_url, comic_name, download_directory, conversion, keep_files):
        short_content = source.findAll('div', {'itemprop': 'description articleBody'})
        img_list = re.findall(r'href="(.*?)"', str(short_content))
        chapter_number = str(str(comic_url).split("/")[-1]).replace(".html", "")

        file_directory = self.create_file_directory(chapter_number, comic_name)
        directory_path = os.path.realpath(str(download_directory) + "/" + str(file_directory))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        links = []
        file_names = []
        for current_chapter, image_link in enumerate(img_list):
            current_chapter += 1
            file_name = str(self.prepend_zeroes(current_chapter, len(img_list))) + ".jpg"
            file_names.append(file_name)
            links.append(image_link)

        self.multithread_download(chapter_number, comic_name, comic_url, directory_path, file_names, links, self.logging)
        self.conversion(directory_path, conversion, keep_files, comic_name, chapter_number)

        return 0

    def full_series(self, source, comic_url, comic_name, sorting, download_directory, chapter_range, conversion,
                    keep_files):
        all_links = re.findall(r'http://striputopija.blogspot.rs/\d+/\d+/\d+|_.html', str(source))

        if chapter_range != "All":
            starting = int(str(chapter_range).split("-")[0]) - 1

            if str(chapter_range).split("-")[1].isdigit():
                ending = int(str(chapter_range).split("-")[1])
            else:
                ending = len(all_links)

            indexes = [x for x in range(starting, ending)]
            all_links = [all_links[x] for x in indexes][::-1]

        if self.print_index:
            all_chapters = re.findall(r'http://striputopija.blogspot.rs/\d+/\d+/.+.html.+>(.+)</a>', str(source))
            for idx, chap_link in enumerate(all_chapters, start=1):
                print(f"{idx}: {chap_link}")
            return

        if str(sorting).lower() in ['new', 'desc', 'descending', 'latest']:
            for chap_link in all_links:
                page_source, cookies_main = self.page_downloader(manga_url=chap_link + ".html")
                try:
                    self.single_chapter(page_source, chap_link + ".html", comic_name, download_directory,
                                        conversion, keep_files)
                except Exception as ex:
                    self.logging.error(f"Error downloading : {chap_link}")
                    break
                if chapter_range != "All" and (
                        chapter_range.split("-")[1] == "__EnD__" or len(chapter_range.split("-")) == 3):
                    self.addOne(comic_url)

        elif str(sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            for chap_link in reversed(all_links):
                page_source, cookies_main = self.page_downloader(manga_url=chap_link + ".html")
                try:
                    self.single_chapter(page_source, chap_link + ".html", comic_name, download_directory,
                                        conversion, keep_files)
                except Exception as ex:
                    self.logging.error(f"Error downloading : {chap_link}")
                    break
                if chapter_range != "All" and (
                        chapter_range.split("-")[1] == "__EnD__" or len(chapter_range.split("-")) == 3):
                    self.addOne(comic_url)

        return 0
