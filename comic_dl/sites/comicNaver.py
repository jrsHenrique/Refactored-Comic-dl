#!/usr/bin/env python
# -*- coding: utf-8 -*-

from comic_dl import globalFunctions
import re
import os
import logging

from comic_dl.sites.mangaDownloader import MangaDownloader


class ComicNaver(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)

        if "/list?" in manga_url or "list.nhn" in manga_url:
            self.full_series()
        elif "/detail?" in manga_url or "detail.nhn" in manga_url:
            self.single_chapter(manga_url)

    def name_cleaner(self, url):
        manga_name = re.search(r"titleId=(\d+)", str(url)).group(1)
        return manga_name

    def user_login(self):
        pass

    def single_chapter(self, comic_url):
        comic_name = self.name_cleaner(comic_url)
        chapter_number = re.search(r"no=(\d+)", str(comic_url)).group(1)

        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_url)
        img_regex = r'https?://(?:imgcomic\.naver\.net|image-comic\.pstatic\.net)/webtoon/\d+/\d+/.+?\.(?:jpg|png|gif|bmp|JPG|PNG|GIF|BMP)'
        image_list = list(re.findall(img_regex, str(source)))

        if not image_list:
            all_image_tags = source.find_all("img", {"alt": "comic content"})
            for img_tag in all_image_tags:
                image_list.append(img_tag['src'])

        logging.debug("Image List : %s" % image_list)

        file_directory = globalFunctions.GlobalFunctions().create_file_directory(chapter_number, comic_name)
        directory_path = os.path.realpath(self.download_directory + "/" + file_directory)

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        links = []
        file_names = []
        for current_chapter, image_link in enumerate(image_list):
            current_chapter += 1
            file_name = str(globalFunctions.GlobalFunctions().prepend_zeroes(current_chapter, len(image_list))) + ".jpg"
            file_names.append(file_name)
            links.append(image_link)

        globalFunctions.GlobalFunctions().multithread_download(chapter_number, comic_name, comic_url, directory_path,
                                                               file_names, links, self.logging)
        globalFunctions.GlobalFunctions().conversion(directory_path, self.conversion, self.keep_files, comic_name,
                                                     chapter_number)

        return 0

    def full_series(self):
        comic_name = self.name_cleaner(self.manga_url)
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=self.manga_url)
        comic_type = re.findall(r"webtoon/(.+?)/", str(self.manga_url))[0]
        latest_chapter = re.findall(r"no=(\d+)[\&|\"]", str(source))[1]
        all_links = []
        for x in range(1, int(latest_chapter) + 1):
            chapter_url = f"http://comic.naver.com/{0}/detail.nhn?titleId={1}&no={2}".format(comic_type, comic_name, x)
            all_links.append(chapter_url)

        logging.debug("All Links : %s" % all_links)

        if self.chapter_range != "All":
            starting = int(self.chapter_range.split("-")[0]) - 1
            ending = int(self.chapter_range.split("-")[1]) if self.chapter_range.split("-")[1].isdigit() else len(all_links)
            all_links = [all_links[x] for x in range(starting, ending)][::-1]

        for chap_link in all_links:
            self.single_chapter(chap_link)