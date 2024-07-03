#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from comic_dl import globalFunctions
from comic_dl.sites.mangaDownloader import MangaDownloader

class ReadComicOnlineLi(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)

    def download_comic(self):
        url_split = str(self.manga_url).split("/")
        self.appended_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'dnt': '1',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'
        }

        if len(url_split) == 5:
            self.full_series(comic_url=self.manga_url.replace("&readType=1", ""), comic_name=self.comic_name,
                             sorting=self.sorting, download_directory=self.download_directory, chapter_range=self.chapter_range,
                             conversion=self.conversion, keep_files=self.keep_files)
        else:
            if "&readType=0" in self.manga_url:
                self.manga_url = str(self.manga_url).replace("&readType=0", "&readType=1")
            self.single_chapter(self.manga_url, self.comic_name, self.download_directory, conversion=self.conversion,
                                keep_files=self.keep_files)

    # You can override any methods here if needed, such as `single_chapter`, `full_series`, etc.
    # Otherwise, they will be inherited from the MangaDownloader class.


# Exemplo de uso:
if __name__ == "__main__":
    manga_url = "http://fanfox.net/manga/vigilante_boku_no_hero_academia_illegals/c000/1.html"
    download_directory = "../../"
    chapter_range = "All"
    
    downloader = ReadComicOnlineLi(manga_url, download_directory, chapter_range)
    downloader.download_comic()