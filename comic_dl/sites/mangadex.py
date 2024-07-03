#!/usr/bin/env python
# -*- coding: utf-8 -*-
from comic_dl import globalFunctions
import os
import logging
import json
from comic_dl.sites.mangaDownloader import MangaDownloader

class Mangadex(MangaDownloader):
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        super().__init__(manga_url, download_directory, chapter_range, **kwargs)

    def name_cleaner(self, url):
        """
        Implements name cleaning for Mangadex.
        """
        # Example cleaning logic
        return "Cleaned Comic Name"

    def single_chapter(self, comic_url):
        """
        Implements downloading a single chapter for Mangadex.
        """
        comic_url = str(comic_url)
        chapter_split = comic_url.split('/')
        chapter_id = chapter_split[-2] if len(chapter_split) > 5 else chapter_split[-1]
        links = []
        file_names = []
        chapter_number = chapter_id

        # Get image info
        api_images = "https://api.mangadex.org/at-home/server/{0}?forcePort443=false".format(chapter_id)
        source_image_list, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=api_images)
        image_info = json.loads(str(source_image_list))
        base_image_url = image_info['baseUrl']
        base_hash = image_info['chapter']['hash']
        images = image_info['chapter']['data']
        
        for idx, image in enumerate(images):
            links.append("{0}/data/{1}/{2}".format(base_image_url, base_hash, image))
            img_extension = str(image).rsplit('.', 1)[-1]
            file_names.append('{0}.{1}'.format(idx, img_extension))
        
        # Get chapter info
        api_chapter_info = "https://api.mangadex.org/chapter/{0}?includes[]=scanlation_group&includes[]=manga&includes[]=user".format(chapter_id)
        source_chapter_info, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=api_chapter_info)
        source_chapter_info = json.loads(str(source_chapter_info))
        
        if source_chapter_info:
            chapter_number = source_chapter_info['data']['attributes']['chapter']
            for relation in source_chapter_info['data']['relationships']:
                if self.comic_name:
                    break
                if relation['type'] == "manga":
                    try:
                        self.comic_name = relation['attributes']['title']['en']
                        break
                    except Exception as NameNotFound:
                        dict_obj = dict(relation['attributes']['title'])
                        for key in dict_obj.keys():
                            self.comic_name = dict_obj[key]
                            break  # Take the first title and break out of loop
        else:
            self.comic_name = chapter_id
        
        file_directory = globalFunctions.GlobalFunctions().create_file_directory(chapter_number, self.comic_name)
        directory_path = os.path.realpath(os.path.join(self.download_directory, file_directory))

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        
        globalFunctions.GlobalFunctions().multithread_download(chapter_number, self.comic_name, comic_url, directory_path, file_names, links, self.logging)
        globalFunctions.GlobalFunctions().conversion(directory_path, self.conversion, self.keep_files, self.comic_name, chapter_number)

        return 0

    def full_series(self):
        """
        Implements downloading a series of comics for Mangadex.
        """
        comic_id = str(self.manga_url).rsplit('/', 2)[-2]
        comic_detail_url = "https://api.mangadex.org/manga/{0}/aggregate?translatedLanguage[]=en".format(comic_id)
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_detail_url)
        source = json.loads(str(source))

        all_links = []
        all_volumes = {}
        volumes = dict(source['volumes'])
        
        for volume in volumes.keys():
            volume_info = dict(volumes[volume])
            chapters = dict(volume_info.get('chapters', {}))
            
            for chapter in chapters.keys():
                chapter = dict(chapters[chapter])
                chapter_url = "https://mangadex.org/chapter/{0}/{1}".format(chapter.get('id'), chapter.get('chapter', 1))
                all_links.append(chapter_url)
                all_volumes[chapter_url] = "Volume {0}".format(volume)

        logging.debug("All Links : {0}".format(all_links))

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
                
                if self.chapter_range != "All" and (self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
                    globalFunctions.GlobalFunctions().addOne(self.manga_url)
                    
        elif str(self.sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            for chap_link in all_links[::-1]:
                try:
                    self.single_chapter(comic_url=chap_link)
                except Exception as ex:
                    logging.error("Error downloading : %s" % chap_link)
                    break
                
                if self.chapter_range != "All" and (self.chapter_range.split("-")[1] == "__EnD__" or len(self.chapter_range.split("-")) == 3):
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
