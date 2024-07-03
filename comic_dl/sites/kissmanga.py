#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
from comic_dl import globalFunctions
from comic_dl.sites.mangaDownloader import MangaDownloader

class KissManga(MangaDownloader):
    def __init__(self, manga_url, download_directory, **kwargs):
        super().__init__(manga_url, download_directory, **kwargs)
        print("Currently Under Development")
        self.comic_name = self.name_cleaner(manga_url)
        self.single_chapter(manga_url)

    def name_cleaner(self, url):
        initial_name = re.search(r"/Manga/(.*?)/", str(url)).group(1)
        safe_name = re.sub(r"[0-9][a-z][A-Z]\ ", "", str(initial_name))
        anime_name = str(safe_name.title()).replace("-", " ")
        return anime_name

    def single_chapter(self, comic_url):
        chapter_number = re.search("(\d+)", str(comic_url)).group(1)
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_url)
        image_list = re.findall(r"lstImages\.push\(wrapKA\(\"(.*?)\"\)\);", str(source))

        file_directory = globalFunctions.GlobalFunctions().create_file_directory(chapter_number, self.comic_name)
        directory_path = os.path.realpath(os.path.join(self.download_directory, file_directory))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        links = []
        file_names = []
        for index, link in enumerate(image_list):
            link_edited = "http://2.bp.blogspot.com/" + link.replace("\\", "") + ".png"
            file_name = f"{index}.jpg"
            
            file_names.append(file_name)
            links.append(link_edited)

        globalFunctions.GlobalFunctions().multithread_download(
            chapter_number, self.comic_name, comic_url, directory_path, file_names, links, self.logging
        )

        return 0
