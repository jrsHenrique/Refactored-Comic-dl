#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from comic_dl import globalFunctions
from comic_dl.sites.mangaDownloader import MangaDownloader

class Manganelo(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)
        self.manga_url = manga_url
        self.sorting = kwargs.get("sorting_order")
        self.print_index = kwargs.get("print_index")
        self.logging = kwargs.get("log_flag")

    def single_chapter(self, manga_url):
        """
        Implements downloading a single chapter for Manganelo.
        """
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=manga_url)

        if "mangakakalot" in manga_url:
            breadcrumb = source.find('div', {'class': 'breadcrumb'})
            breadcrumb_parts = breadcrumb.findAll('a')
            comic_name = (breadcrumb_parts[1])['title']
            chapter_number = (breadcrumb_parts[2]).find('span').text
        else:  # manganelo.com, manganato.com, readmanganato.com, chapmanganato.com
            breadcrumb = source.find('div', {'class': 'panel-breadcrumb'})
            breadcrumb_parts = breadcrumb.findAll('a')
            comic_name = (breadcrumb_parts[1])['title']
            chapter_number = (breadcrumb_parts[2])['title']

        file_directory = globalFunctions.GlobalFunctions().create_file_directory(chapter_number, comic_name)
        directory_path = os.path.realpath(os.path.join(self.download_directory, file_directory))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        images = source.findAll('img')

        links = []
        file_names = []
        i = 0
        for image in images:
            image_link = image['src']

            if "/themes/" in image_link:
                continue

            file_name = str(globalFunctions.GlobalFunctions().prepend_zeroes(i, len(images))) + ".jpg"
            file_names.append(file_name)
            links.append(image_link)
            i += 1

        try:
            globalFunctions.GlobalFunctions().multithread_download(chapter_number, comic_name, manga_url,
                                                                   directory_path,
                                                                   file_names, links, self.logging)
        except Exception as ex:
            # Handle mirror server logic if initial download fails
            found_mirrors = source.find("a", {"data-l": True})
            if found_mirrors:
                mirror_url = found_mirrors['data-l']
                self.single_chapter(manga_url=mirror_url)

        globalFunctions.GlobalFunctions().conversion(directory_path, self.conversion, self.keep_files, comic_name,
                                                     chapter_number)

        return 0

    def full_series(self):
        """
        Implements downloading a series of comics for Manganelo.
        """
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=self.manga_url)

        if "mangakakalot" in self.manga_url:
            chapter_list = source.find('div', {'class': 'chapter-list'})
            all_links = chapter_list.findAll('a')
        else:  # manganelo.com, manganato.com, readmanganato.com
            chapter_list = source.find('ul', {'class': 'row-content-chapter'})
            if chapter_list is None:
                raise Exception('no chapter found')
            all_links = chapter_list.findAll('a')

        chapter_links = [link['href'] for link in all_links]

        if self.chapter_range != "All":
            starting = int(str(self.chapter_range).split("-")[0]) - 1

            if str(self.chapter_range).split("-")[1].isdigit():
                ending = int(str(self.chapter_range).split("-")[1])
            else:
                ending = len(all_links)

            indexes = [x for x in range(starting, ending)]
            chapter_links = [chapter_links[x] for x in indexes][::-1]

        if self.print_index:
            idx = len(chapter_links)
            for idx, chap_link in enumerate(chapter_links, start=1):
                print(f"{idx}: {chap_link}")

        for chap_link in chapter_links:
            try:
                self.single_chapter(manga_url=str(chap_link))
            except Exception as ex:
                self.logging.error(f"Error downloading: {chap_link}")

        return 0

    def user_login(self):
        """
        Placeholder for user login implementation if needed.
        """
        # Implement user login logic here if required
        pass
