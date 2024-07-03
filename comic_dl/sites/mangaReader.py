#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from comic_dl import globalFunctions
from comic_dl.sites.mangaDownloader import MangaDownloader

class MangaReader(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)
        self.logging = kwargs.get("log_flag")
        self.sorting = kwargs.get("sorting_order")
        self.comic_name = self.name_cleaner(manga_url)
        self.print_index = kwargs.get("print_index")

        if self.is_listing_page(manga_url):
            self.full_series(comic_url=manga_url, comic_name=self.comic_name,
                             sorting=self.sorting, download_directory=download_directory, chapter_range=chapter_range,
                             conversion=kwargs.get("conversion"), keep_files=kwargs.get("keep_files"))
        else:
            self.single_chapter(manga_url, self.comic_name, download_directory, conversion=kwargs.get("conversion"),
                                keep_files=kwargs.get("keep_files"))

    def name_cleaner(self, url):
        return str(url.split("/")[3].strip().replace("-", " ").title())

    def is_listing_page(self, manga_url):
        url_parts = manga_url.split("/")
        return len(url_parts) < 5 or (len(url_parts) == 5 and not url_parts[-1])

    def single_chapter(self, comic_url, comic_name, download_directory, conversion, keep_files):
        chapter_number = int(comic_url.split("/")[4])
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_url)

        total_pages = int(re.search(r'</select> of (.*?)</div>', str(source)).group(1).strip())

        file_directory = globalFunctions.GlobalFunctions().create_file_directory(chapter_number, comic_name)
        directory_path = os.path.realpath(os.path.join(download_directory, file_directory))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        links = []
        file_names = []
        for page_number in range(1, total_pages + 1):
            next_url = f"{comic_url}/{page_number}"
            next_source, next_cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=next_url,
                                                                                          cookies=cookies)
            img_holder_div = next_source.find_all('div', {'id': 'imgholder'})

            for single_node in img_holder_div:
                x = single_node.findAll('img')
                for a in x:
                    image_link = str(a['src']).strip()
                    file_name = str(globalFunctions.GlobalFunctions().prepend_zeroes(page_number, total_pages)) + ".jpg"
                    links.append(image_link)
                    file_names.append(file_name)

        globalFunctions.GlobalFunctions().multithread_download(chapter_number, comic_name, comic_url, directory_path,
                                                               file_names, links, self.logging)

        globalFunctions.GlobalFunctions().conversion(directory_path, conversion, keep_files,
                                                     comic_name, chapter_number)

    def full_series(self, comic_url, comic_name, sorting, download_directory, chapter_range, conversion, keep_files):
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_url)
        all_links = []

        chap_holder_div = source.find_all('table', {'id': 'listing'})

        for single_node in chap_holder_div:
            x = single_node.findAll('a')
            for a in x:
                all_links.append("http://www.mangareader.net" + str(a['href']).strip())
        logging.debug("all_links : %s" % all_links)

        if chapter_range != "All":
            starting = int(str(chapter_range).split("-")[0]) - 1

            if str(chapter_range).split("-")[1].isdigit():
                ending = int(str(chapter_range).split("-")[1])
            else:
                ending = len(all_links)

            indexes = [x for x in range(starting, ending)]
            all_links = [all_links[x] for x in indexes][::-1]
        else:
            all_links = all_links

        if self.print_index:
            idx = 0
            for chap_link in all_links:
                idx = idx + 1
                print(str(idx) + ": " + chap_link)
            return

        if str(sorting).lower() in ['new', 'desc', 'descending', 'latest']:
            for chap_link in all_links:
                try:
                    self.single_chapter(comic_url=chap_link, comic_name=comic_name,
                                        download_directory=download_directory,
                                        conversion=conversion, keep_files=keep_files)
                except Exception as ex:
                    logging.error("Error downloading : %s" % chap_link)
                    break

                if chapter_range != "All" and (chapter_range.split("-")[1] == "__EnD__" or len(chapter_range.split("-")) == 3):
                    globalFunctions.GlobalFunctions().addOne(comic_url)

        elif str(sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            for chap_link in all_links[::-1]:
                try:
                    self.single_chapter(comic_url=chap_link, comic_name=comic_name,
                                        download_directory=download_directory,
                                        conversion=conversion, keep_files=keep_files)
                except Exception as ex:
                    logging.error("Error downloading : %s" % chap_link)
                    break

                if chapter_range != "All" and (chapter_range.split("-")[1] == "__EnD__" or len(chapter_range.split("-")) == 3):
                    globalFunctions.GlobalFunctions().addOne(comic_url)

        return 0
