#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tqdm import tqdm
from .__version__ import __version__
import argparse
import logging
import sys
import platform
from . import honcho
import os
import time
import json
from . import configGenerator
from .readcomiconline import RCO
from .readcomiconline import dataUpdate

CONFIG_FILE = 'config.json'


class ArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Comic_dl is a command line tool to download comics and manga from various such sites.')
        self.add_arguments()
        self.args = self.parser.parse_args()

    def add_arguments(self):
        self.parser.add_argument('--version', action='store_true', help='Shows version and exits.')
        self.parser.add_argument('-s', '--sorting', nargs=1, help='Decides downloading order of chapters.')
        self.parser.add_argument('-a', '--auto', action='store_true', help='Download new chapters automatically (needs config file!)')
        self.parser.add_argument('-c', '--config', action='store_true', help='Generates config file for autodownload function')
        self.parser.add_argument('-dd', '--download-directory', nargs=1, help='Decides the download directory of the comics/manga.', default=[os.getcwd()])
        self.parser.add_argument('-rn', '--range', nargs=1, help='Specifies the range of chapters to download.', default='All')
        self.parser.add_argument('--convert', nargs=1, help='Tells the script to convert the downloaded Images to PDF or anything else.')
        self.parser.add_argument('--keep', nargs=1, help='Tells the script whether to keep the files after conversion or not.', default=['True'])
        self.parser.add_argument('--quality', nargs=1, help='Tells the script which Quality of image to download (High/Low).', default='True')
        self.parser.add_argument('-i', '--input', nargs=1, help='Inputs the URL to comic.')
        self.parser.add_argument('-cookie', '--cookie', nargs=1, help='Passes cookie (text format) to be used throughout the session.')
        self.parser.add_argument("--comic", action="store_true", help="Add this after -i if you are inputting a comic id or the EXACT comic name.")
        self.parser.add_argument("-comic-search", "--search-comic", nargs=1, help="Searches for a comic through the gathered data from ReadComicOnline.to")
        self.parser.add_argument("-comic-info", "--comic-info", nargs=1, help="List all informations for the queried comic.")
        self.parser.add_argument("--update", nargs=1, help="USAGE: --update <COMIC_LINK OR COMIC_NAME>... Updates the comic database for the given argument.")
        self.parser.add_argument('--print-index', action='store_true', help='prints the range index for links in the input URL')
        self.parser.add_argument('-ml', '--manga-language', nargs=1, help='Selects the language for manga.', default='0')
        self.parser.add_argument('-sc', '--skip-cache', nargs=1, help='Forces to skip cache checking.', default='0')
        self.parser.add_argument('-p', '--password', nargs=1, help='Takes Password used to log into a website, along with a username/email.', default=['None'])
        self.parser.add_argument('-u', '--username', nargs=1, help='Takes username/email used to log into a website, along with a password.', default=['None'])
        self.parser.add_argument("-v", "--verbose", help="Prints important debugging messages on screen.", action="store_true")


class LoggerSetup:
    def __init__(self, args):
        self.args = args
        self.logger = False
        if self.args.verbose:
            self.setup_verbose_mode()

    def setup_verbose_mode(self):
        print("\n***Starting the script in Verbose Mode***\n")
        try:
            os.remove("Error_Log.log")
        except Exception:
            pass
        logging.basicConfig(format='%(levelname)s: %(message)s',
                            filename=str(self.args.download_directory[0]) + str(os.sep) + "Error_Log.log",
                            level=logging.DEBUG)
        logging.debug("Arguments Provided : %s" % self.args)
        logging.debug("Operating System : %s - %s - %s" % (platform.system(),
                                                           platform.release(),
                                                           platform.version()
                                                           ))
        logging.debug("Python Version : %s (%s)" % (platform.python_version(), platform.architecture()[0]))
        logging.debug("Script Version : {0}".format(__version__))
        self.logger = True


class ComicDL:
    def __init__(self, argv):
        self.args = ArgumentParser().args
        self.logger_setup = LoggerSetup(self.args)
        self.logger = self.logger_setup.logger

        if self.args.version:
            self.version()
            sys.exit()

        if self.args.comic_info or self.args.search_comic:
            self.handle_comic_search_info()
            sys.exit()

        if self.args.update:
            self.update_comic_database()

        if self.args.auto:
            self.auto_download()
            sys.exit()

        if self.args.config:
            self.generate_config()
            sys.exit()

        if self.args.input is None:
            print("I need an Input URL to download from.")
            print("Run the script with --help to see more information.")
        else:
            self.download_comic()

    @staticmethod
    def version():
        print(__version__)

    def handle_comic_search_info(self):
        rco = RCO.ReadComicOnline()
        if self.args.search_comic:
            query = self.args.search_comic[0]
            rco.comicSearch(query)
        elif self.args.comic_info:
            query = self.args.comic_info[0]
            rco.comicInfo(query)

    def update_comic_database(self):
        query = self.args.update[0]
        if "readcomiconline" in query or "https://" in query or "http://" in query:
            dataUpdate.RCOUpdater(link=query)
        else:
            dataUpdate.RCOUpdater(name=query)

    def auto_download(self):
        data = json.load(open(CONFIG_FILE))
        sorting_order = "ascending"
        download_directory = data["download_directory"]
        conversion = data["conversion"]
        keep_files = data["keep"]
        image_quality = data["image_quality"]
        manual_cookie = data["cookie"] if "cookie" in data else None
        pbar_comic = tqdm(data["comics"], dynamic_ncols=True, desc="[Comic-dl] Auto processing", leave=True,
                          unit='comic')
        for elKey in pbar_comic:
            try:
                pbar_comic.set_postfix(comic_name=elKey)
                el = data["comics"][elKey]
                download_range = str(el["next"]) + "-__EnD__"
                if "last" in el and not el["last"] == "None":
                    download_range = str(el["next"]) + "-" + str(el["last"]) + "-RANGE"

                honcho.Honcho().checker(comic_url=el["url"].strip(), current_directory=os.getcwd(),
                                        sorting_order=sorting_order, logger=self.logger,
                                        download_directory=download_directory,
                                        chapter_range=download_range, conversion=conversion,
                                        keep_files=keep_files, image_quality=image_quality,
                                        username=el["username"], password=el["password"],
                                        comic_language=el["comic_language"],
                                        cookie=manual_cookie)
            except Exception as ex:
                pbar_comic.write('[Comic-dl] Auto processing with error for %s : %s ' % (elKey, ex))
        pbar_comic.set_postfix()
        pbar_comic.close()

    def generate_config(self):
        configGenerator.configGenerator()

    def download_comic(self):
        print_index = self.args.print_index
        manual_cookie = self.args.cookie[0] if self.args.cookie else None

        if not self.args.sorting:
            self.args.sorting = ["ascending"]
        if not self.args.download_directory:
            self.args.download_directory = [os.getcwd()]
        if type(self.args.range) == list:
            self.args.range = self.args.range[0]
        if not self.args.convert:
            self.args.convert = ["None"]
        if not self.args.keep:
            self.args.keep = ["True"]
        if not self.args.quality or self.args.quality == "True":
            self.args.quality = ["Best"]

        user_input = self.args.input[0]

        if self.args.comic:
            rco = RCO.ReadComicOnline()
            user_input = rco.comicLink(user_input)

            if not user_input:
                print("No comic found with that name or id.")
                print("If you are inputting an ID, use -comic-search <QUERY> to determine the id.")
                print("If you are inputting a name, you must input the exact name of the comic for ")
                sys.exit()

        start_time = time.time()
        honcho.Honcho().checker(comic_url=user_input, current_directory=os.getcwd(),
                                sorting_order=self.args.sorting[0], logger=self.logger,
                                download_directory=self.args.download_directory[0],
                                chapter_range=self.args.range, conversion=self.args.convert[0],
                                keep_files=self.args.keep[0], image_quality=self.args.quality[0],
                                username=self.args.username[0], password=self.args.password[0],
                                comic_language=self.args.manga_language[0], print_index=print_index,
                                cookie=manual_cookie)
        end_time = time.time()
        total_time = end_time - start_time
        print("Total Time Taken To Complete : %s" % total_time)
        sys.exit()


if __name__ == '__main__':
    ComicDL(sys.argv)
