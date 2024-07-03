#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from comic_dl import globalFunctions
from comic_dl.sites.mangaDownloader import MangaDownloader

class Webtoons(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)
        self.quality = kwargs.get("image_quality", "Best")
        self.logging = kwargs.get("log_flag")
        self.sorting = kwargs.get("sorting_order")
        self.print_index = kwargs.get("print_index")

        if "/viewer?" in manga_url:
            self.single_chapter(manga_url, download_directory, self.conversion, self.keep_files)
        else:
            self.full_series(manga_url, self.sorting, download_directory, chapter_range, self.conversion, self.keep_files)

    def single_chapter(self, manga_url, download_directory, conversion, keep_files):
        url_splitter = str(manga_url).split('?')[-1].split('&')
        chapter_number = 0
        comic_name = globalFunctions.easySlug(str(manga_url).split('/')[5].replace('-', ' ').title())
        for param in url_splitter:
            if "episode_no" in param.lower().strip():
                chapter_number = param.split("=")[-1]
                break
        page_source, cookies = self.page_downloader(manga_url=manga_url)

        file_directory = self.create_file_directory(chapter_number, comic_name)
        directory_path = os.path.realpath(str(download_directory) + os.sep + str(file_directory))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        images = page_source.findAll('img')

        links = []
        file_names = []
        i = 0
        chapter_list = page_source.find('div', {'id': '_imageList'})
        all_links = chapter_list.findAll('img')
        for link in all_links:
            file_name = str(self.prepend_zeroes(i, len(images))) + ".jpg"
            file_names.append(file_name)
            links.append(str(link['data-url']).replace('type=q90', '') if self.quality.lower().strip() == "best" else link['data-url'])
            i += 1

        self.multithread_download(chapter_number, comic_name, manga_url, directory_path, file_names, links, self.logging)

        self.conversion(directory_path, conversion, keep_files, comic_name, chapter_number)

        return 0

    def full_series(self, comic_url, sorting, download_directory, chapter_range, conversion, keep_files):
        page_source, cookies = self.page_downloader(manga_url=comic_url)
        page_list = page_source.find('div', {'class': 'detail_lst'})
        all_pages = page_list.findAll('a')
        all_pages_link = []
        for page in all_pages:
            if "/list?" in page["href"]:
                current_page_url = f"https://www.webtoons.com{page['href'].replace('&amp;', '&').strip()}"
                all_pages_link.append(current_page_url)

        all_links = []
        for page_link in all_pages_link:
            page_source, cookies = self.page_downloader(manga_url=page_link, cookies=cookies)
            all_links += self.extract_chapter_links(page_source)

        if chapter_range != "All":
            starting = int(chapter_range.split("-")[0]) - 1

            if chapter_range.split("-")[1].isdigit():
                ending = int(chapter_range.split("-")[1])
            else:
                ending = len(all_links)

            indexes = [x for x in range(starting, ending)]
            chapter_links = [all_links[x] for x in indexes][::-1]
        else:
            chapter_links = all_links

        if self.print_index:
            for idx, chap_link in enumerate(chapter_links, start=1):
                print(f"{idx}: {chap_link}")
            return

        if str(sorting).lower() in ['new', 'desc', 'descending', 'latest']:
            for chap_link in chapter_links:
                try:
                    self.single_chapter(chap_link, download_directory, conversion, keep_files)
                except Exception as ex:
                    self.logging.error(f"Error downloading : {chap_link}")
                    break
                if chapter_range != "All" and (
                        chapter_range.split("-")[1] == "__EnD__" or len(chapter_range.split("-")) == 3):
                    self.addOne(comic_url)

        elif str(sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            for chap_link in reversed(chapter_links):
                try:
                    self.single_chapter(chap_link, download_directory, conversion, keep_files)
                except Exception as ex:
                    self.logging.error(f"Error downloading : {chap_link}")
                    break
                if chapter_range != "All" and (
                        chapter_range.split("-")[1] == "__EnD__" or len(chapter_range.split("-")) == 3):
                    self.addOne(comic_url)

        return 0

    def extract_chapter_links(self, source):
        chapter_list = source.find('ul', {'id': '_listUl'})
        all_links = chapter_list.findAll('a', href=True)
        chapter_links = [link['href'] for link in all_links]
        return chapter_links
