#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from comic_dl import globalFunctions
from comic_dl.sites.mangaDownloader import MangaDownloader

class MangatoonMobi(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)

    def download_full_series(self):
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=self.manga_url)

        all_chapter_links = source.find_all("a", {"class": "episode-item-new"})
        all_links = [f"https://mangatoon.mobi{chapter['href']}" for chapter in all_chapter_links]

        if self.chapter_range != "All":
            start_idx, end_idx = map(int, self.chapter_range.split("-"))
            all_links = all_links[start_idx - 1:end_idx][::-1]

        if self.print_index:
            for idx, chap_link in enumerate(all_links, start=1):
                print(f"{idx}: {chap_link}")
            return

        if str(self.sorting).lower() in ['new', 'desc', 'descending', 'latest']:
            for chap_link in all_links:
                try:
                    self.manga_url = chap_link
                    self.download_single_chapter()
                except Exception as ex:
                    logging.error(f"Error downloading : {chap_link}")
                    break
                if self.chapter_range != "All" and (self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                    globalFunctions.GlobalFunctions().addOne(self.manga_url)

        elif str(self.sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            for chap_link in reversed(all_links):
                try:
                    self.manga_url = chap_link
                    self.download_single_chapter()
                except Exception as ex:
                    logging.error(f"Error downloading : {chap_link}")
                    break
                if self.chapter_range != "All" and (self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                    globalFunctions.GlobalFunctions().addOne(self.manga_url)

