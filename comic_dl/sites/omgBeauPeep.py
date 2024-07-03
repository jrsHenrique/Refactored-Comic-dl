#!/usr/bin/env python
# -*- coding: utf-8 -*-

from comic_dl import globalFunctions
import os
import logging
import json
from comic_dl.sites.mangaDownloader import MangaDownloader

class OmgBeauPeep(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)

    def download_single_chapter(self):
        chapter_number = self.manga_url.rsplit('/', 1)[-1]
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=self.manga_url)

        last_page_number = int(re.search(r"</select> of (\d+) <a", str(source)).group(1))

        file_directory = globalFunctions.GlobalFunctions().create_file_directory(chapter_number, self.comic_name)
        directory_path = os.path.realpath(str(self.download_directory) + "/" + str(file_directory))

        if self.print_index:
            for x in range(1, last_page_number + 1):
                print(f"{x}: {self.manga_url}/{x}")
            return

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        links = []
        file_names = []
        for x in range(1, last_page_number + 1):
            chapter_url = f"{self.manga_url}/{x}"
            image_prefix = "http://www.omgbeaupeep.com/comics/mangas/"
            if "otakusmash" in self.manga_url:
                image_prefix = "https://www.otakusmash.com/read-comics/mangas/"
            source_new, cookies_new = globalFunctions.GlobalFunctions().page_downloader(manga_url=chapter_url)
            image_link = image_prefix + str(re.search(r'"mangas/(.*?)"', str(source_new)).group(1)).replace(" ", "%20")
            logging.debug(f"Chapter Url : {chapter_url}")
            logging.debug(f"Image Link : {image_link}")
            file_name = f"{globalFunctions.GlobalFunctions().prepend_zeroes(x, last_page_number + 1)}.jpg"

            links.append(image_link)
            file_names.append(file_name)

        globalFunctions.GlobalFunctions().multithread_download(chapter_number, self.comic_name, self.manga_url,
                                                               directory_path, file_names, links, self.logging)

        globalFunctions.GlobalFunctions().conversion(directory_path, self.conversion, self.keep_files,
                                                     self.comic_name, chapter_number)

    def download_full_series(self):
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=self.manga_url)

        chapters = source.find_all('select', {'name': 'chapter'})[0]
        bypass_first = "otakusmash" in self.manga_url
        for option in chapters.find_all('option'):
            if self.print_index:
                print('{}: {}'.format(option['value'], option.text))
            else:
                if bypass_first:  # Because this website lists the next chapter, which is NOT available.
                    bypass_first = False
                    continue
                try:
                    self.manga_url = f"{self.manga_url}/{option['value']}"
                    self.download_single_chapter()
                except Exception as ex:
                    logging.error(f"Error downloading : {option['value']}")
                    break
