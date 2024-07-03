#!/usr/bin/env python
# -*- coding: utf-8 -*-

from comic_dl import globalFunctions
import re
import os
from comic_dl.sites.mangaDownloader import MangaDownloader


class ReadComicBooksOnline(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)

    def download_single_chapter(self):
        chapter_number = int(str(self.manga_url).replace("/", "").split("_")[-1].strip())
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=self.manga_url)

        try:
            first_image_link = "http://readcomicbooksonline.net/reader/mangas" + \
                               str(re.search(r'src="mangas(.*?)\"', str(source)).group(1)).replace(" ", "%20")
        except:
            print("Seems like this page doesn't Exist.")
            print("Or, there's some issue. Open a new 'ISSUE' on Github.")
            return 1

        last_page_number = int(str(re.search(r'</select> of (.*?) <a', str(source)).group(1)).strip())
        img_list = []
        img_list.append(first_image_link)

        for page_number in range(1, last_page_number):
            image_number = first_image_link[-7:].replace(".jpg", "").replace(".png", "").strip()
            image_number_string = str(int(image_number) + 1).zfill(3) + ".jpg"
            image_download_link = first_image_link.replace(image_number + ".jpg", image_number_string)
            first_image_link = image_download_link
            img_list.append(image_download_link)

        file_directory = globalFunctions.GlobalFunctions().create_file_directory(chapter_number, self.comic_name)
        directory_path = os.path.realpath(str(self.download_directory) + "/" + str(file_directory))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        links = []
        file_names = []
        for current_chapter, image_link in enumerate(img_list):
            current_chapter += 1
            file_name = str(globalFunctions.GlobalFunctions().prepend_zeroes(current_chapter, len(img_list))) + ".jpg"
            file_names.append(file_name)
            links.append(image_link)

        globalFunctions.GlobalFunctions().multithread_download(chapter_number, self.comic_name, self.manga_url,
                                                               directory_path, file_names, links, self.logging)

        globalFunctions.GlobalFunctions().conversion(directory_path, self.conversion, self.keep_files,
                                                     self.comic_name, chapter_number)

        return 0

    def download_full_series(self):
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=self.manga_url)
        all_links = []
        chap_holder_div = source.find_all('div', {'id': 'chapterlist'})

        for single_node in chap_holder_div:
            x = single_node.findAll('a')
            for a in x:
                all_links.append(str(a['href']).strip())

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
            print("Couldn't Find the chapter list")
            return 1

        if self.print_index:
            idx = len(all_links)
            for chap_link in all_links:
                print(str(idx) + ": " + chap_link)
                idx = idx - 1
            return

        if str(self.sorting).lower() in ['new', 'desc', 'descending', 'latest']:
            for chap_link in all_links:
                try:
                    self.download_single_chapter()
                    if self.chapter_range != "All" and (
                            self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                        globalFunctions.GlobalFunctions().addOne(self.manga_url)
                except Exception as ex:
                    break

        elif str(self.sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            for chap_link in all_links[::-1]:
                try:
                    self.download_single_chapter()
                    if self.chapter_range != "All" and (
                            self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                        globalFunctions.GlobalFunctions().addOne(self.manga_url)
                except Exception as e:
                    break

        return 0
