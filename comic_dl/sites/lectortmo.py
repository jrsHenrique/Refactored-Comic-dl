#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import sys

from comic_dl import globalFunctions
import os
import logging
import json
import time
from comic_dl.sites.mangaDownloader import MangaDownloader


class LectorTmo(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)

    def name_cleaner(self, url):
        """
        Implements name cleaning for LectorTmo.
        """
        # Example cleaning logic
        return "Cleaned Comic Name"

    def single_chapter(self, comic_url):
        """
        Implements downloading a single chapter for LectorTmo.
        """
        comic_url = str(comic_url)
        chapter_number = comic_url.split('/')[-1] if "/view_uploads/" in comic_url else comic_url.split('/')[-3]

        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_url)
        ld_json_content = source.find_all("script", {"type": "application/ld+json"})
        if len(ld_json_content) > 0:
            cleaned_json_string = ld_json_content[0].next.strip().replace('\n', '')
            loaded_json = json.loads(cleaned_json_string)
            if loaded_json:
                self.comic_name = loaded_json['headline']

        links = []
        file_names = []
        img_url = self.extract_image_link_from_html(source=source)
        links.append(img_url)
        img_extension = str(img_url).rsplit('.', 1)[-1]
        unique_id = str(img_url).split('/')[-2]
        file_names.append('{0}.{1}'.format(1, img_extension))

        total_page_list = source.find("select", {"id": "viewer-pages-select"})
        last_page_number = 0
        options = total_page_list.findAll('option')
        if len(options) > 0:
            last_page_number = int(options[-1]['value'])
        if last_page_number <= 0:
            print("Couldn't find all the pages. Exiting.")
            sys.exit(1)

        for page_number in range(2, last_page_number + 1):
            current_url = "https://lectortmo.com/viewer/{0}/paginated/{1}".format(unique_id, page_number)
            print("Grabbing details for: {0}".format(current_url))
            source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=current_url, cookies=cookies)
            image_url = self.extract_image_link_from_html(source=source)
            links.append(image_url)
            img_extension = str(image_url).rsplit('.', 1)[-1]
            file_names.append('{0}.{1}'.format(page_number, img_extension))
            time.sleep(random.randint(1, 6))

        directory_path = os.path.realpath(os.path.join(self.download_directory, globalFunctions.GlobalFunctions().create_file_directory(chapter_number, self.comic_name)))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        self.download_chapter(chapter_number, self.comic_name, comic_url, file_names, links)
        globalFunctions.GlobalFunctions().conversion(directory_path, self.conversion, self.keep_files, self.comic_name, chapter_number)

        return 0

    def full_series(self):
        """
        Implements downloading a series of comics for LectorTmo.
        """
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=self.manga_url)

        all_links = []
        all_chapter_links = source.find_all("a", {"class": "btn btn-default btn-sm"})
        for chapter in all_chapter_links:
            all_links.append(chapter['href'])

        logging.debug("All Links : %s" % all_links)

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

        if self.print_index:
            idx = 0
            for chap_link in all_links:
                idx = idx + 1
                print(str(idx) + ": " + chap_link)
            return

        if str(self.sorting).lower() in ['new', 'desc', 'descending', 'latest']:
            for chap_link in all_links:
                try:
                    self.single_chapter(comic_url=chap_link)
                except Exception as ex:
                    logging.error("Error downloading : %s" % chap_link)
                    break
                if self.chapter_range != "All" and (
                        self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                    globalFunctions.GlobalFunctions().addOne(self.manga_url)
        elif str(self.sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            for chap_link in all_links[::-1]:
                try:
                    self.single_chapter(comic_url=chap_link)
                except Exception as ex:
                    logging.error("Error downloading : %s" % chap_link)
                    break
                if self.chapter_range != "All" and (
                        self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                    globalFunctions.GlobalFunctions().addOne(self.manga_url)

        return 0

    def extract_image_link_from_html(self, source):
        image_tags = source.find_all("img", {"class": "viewer-image viewer-page"})
        img_link = None
        for element in image_tags:
            img_link = element['src']
        return img_link

    def user_login(self):
        """
        Placeholder for user login implementation if needed.
        """
        # Implement user login logic here if required
        pass
