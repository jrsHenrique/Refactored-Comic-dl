#!/usr/bin/env python
# -*- coding: utf-8 -*-

from comic_dl import globalFunctions
import os
from comic_dl.sites.mangaDownloader import MangaDownloader

class ReadComicsIO(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)
        self.sorting = kwargs.get("sorting_order")
        self.print_index = kwargs.get("print_index")

    def name_cleaner(self, url):
        manga_name = str(str(url).split("/")[3].strip().replace("_", " ").replace("-", " ").title())
        return manga_name

    def is_full_series(self, url):
        return "/comic/" in url

    def single_chapter(self, comic_url, comic_name, download_directory, conversion, keep_files):
        chapter_number = str(str(comic_url).split("/")[4].strip().replace("_", " ").replace("-", " ").title())
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_url)
        img_list = []
        temp_list = source.find_all("div", {"class": "chapter-container"})
        for elements in temp_list:
            x = elements.findAll('img')
            for a in x:
                img_list.append(str(a['src']).strip())

        file_directory = globalFunctions.GlobalFunctions().create_file_directory(chapter_number, comic_name)
        directory_path = os.path.realpath(str(download_directory) + "/" + str(file_directory))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        links = []
        file_names = []
        for current_chapter, image_link in enumerate(img_list):
            current_chapter += 1
            file_name = str(globalFunctions.GlobalFunctions().prepend_zeroes(current_chapter, len(img_list))) + ".jpg"

            file_names.append(file_name)
            links.append(image_link)

        globalFunctions.GlobalFunctions().multithread_download(chapter_number, comic_name, comic_url, directory_path,
                                                               file_names, links, self.logging)
            
        globalFunctions.GlobalFunctions().conversion(directory_path, conversion, keep_files, comic_name,
                                                     chapter_number)

        return 0

    def full_series(self, comic_url, comic_name, sorting, download_directory, chapter_range, conversion, keep_files):
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_url)
        all_links = []
        chap_holder_div = source.find_all('ul', {'class': 'basic-list'})
        # print(comic_name)
        for single_node in chap_holder_div:
            x = single_node.findAll('a')
            for a in x:
                all_links.append(str(a['href']).strip())
        if chapter_range != "All":
            # -1 to shift the episode number accordingly to the INDEX of it. List starts from 0 xD!
            starting = int(str(chapter_range).split("-")[0]) - 1

            if str(chapter_range).split("-")[1].isdigit():
                ending = int(str(chapter_range).split("-")[1])
            else:
                ending = len(all_links)

            indexes = [x for x in range(starting, ending)]

            all_links = [all_links[x] for x in indexes][::-1]
        else:
            all_links = all_links
        if not all_links:
            print("Couldn't Find the chapter list")
            return 1
        # all_links.pop(0) # Because this website lists the next chapter, which is NOT available.

        if self.print_index:
            idx = 0
            for chap_link in all_links:
                idx = idx + 1
                print(str(idx) + ": " + str(chap_link))
            return

        if str(sorting).lower() in ['new', 'desc', 'descending', 'latest']:
            for chap_link in all_links:
                try:
                    self.single_chapter(comic_url=str(chap_link) + "/full", comic_name=comic_name,
                                        download_directory=download_directory,
                                        conversion=conversion, keep_files=keep_files)
                    # if chapter range contains "__EnD__" write new value to config.json
                    # @Chr1st-oo - modified condition due to some changes on automatic download and config.
                    if chapter_range != "All" and (chapter_range.split("-")[1] == "__EnD__" or len(chapter_range.split("-")) == 3):
                        globalFunctions.GlobalFunctions().addOne(comic_url)
                except Exception as e:
                    break  # break to continue processing other mangas

        elif str(sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            for chap_link in all_links[::-1]:
                try:
                    self.single_chapter(comic_url=str(chap_link) + "/full", comic_name=comic_name,
                                        download_directory=download_directory,
                                        conversion=conversion, keep_files=keep_files)
                    # if chapter range contains "__EnD__" write new value to config.json
                    # @Chr1st-oo - modified condition due to some changes on automatic download and config.
                    if chapter_range != "All" and (chapter_range.split("-")[1] == "__EnD__" or len(chapter_range.split("-")) == 3):
                        globalFunctions.GlobalFunctions().addOne(comic_url)
                except Exception as e:
                    break  # break to continue processing other mangas

        return 0
