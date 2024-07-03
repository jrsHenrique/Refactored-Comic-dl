#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from urllib.parse import urlparse
from .sites import (foolSlide, readcomicOnlineli, comicNaver, mangaHere, rawSenManga, mangaFox,
                    omgBeauPeep, mangaReader, acQQ, stripUtopia, readComicBooksOnline, readComicsWebsite,
                    batoto, hqbr, comicextra, readComicsIO, japscan, manganelo, webtoons, lectortmo,
                    mangatoonMobi, mangadex, quiremanhua)

class Honcho(object):
    def __init__(self):
        self.site_map = {
            "yomanga.co": foolSlide.FoolSlide,
            "gomanga.co": foolSlide.FoolSlide,
            "www.readcomiconline.li": readcomicOnlineli.ReadComicOnlineLi,
            "readcomiconline.li": readcomicOnlineli.ReadComicOnlineLi,
            "www.readcomicsonline.ru": readcomicOnlineli.ReadComicOnlineLi,
            "readcomicsonline.ru": readcomicOnlineli.ReadComicOnlineLi,
            "www.comic.naver.com": comicNaver.ComicNaver,
            "comic.naver.com": comicNaver.ComicNaver,
            "www.mangahere.co": mangaHere.MangaHere,
            "mangahere.co": mangaHere.MangaHere,
            "www.mangahere.cc": mangaHere.MangaHere,
            "mangahere.cc": mangaHere.MangaHere,
            "www.raw.senmanga.com": rawSenManga.RawSenaManga,
            "raw.senmanga.com": rawSenManga.RawSenaManga,
            "www.mangafox.me": mangaFox.MangaFox,
            "mangafox.me": mangaFox.MangaFox,
            "www.mangafox.la": mangaFox.MangaFox,
            "mangafox.la": mangaFox.MangaFox,
            "www.fanfox.net": mangaFox.MangaFox,
            "fanfox.net": mangaFox.MangaFox,
            "www.omgbeaupeep.com": omgBeauPeep.OmgBeauPeep,
            "omgbeaupeep.com": omgBeauPeep.OmgBeauPeep,
            "www.otakusmash.com": omgBeauPeep.OmgBeauPeep,
            "otakusmash.com": omgBeauPeep.OmgBeauPeep,
            "www.ac.qq.com": acQQ.AcQq,
            "ac.qq.com": acQQ.AcQq,
            "www.striputopija.blogspot.in": stripUtopia.StripUtopia,
            "striputopija.blogspot.in": stripUtopia.StripUtopia,
            "www.striputopija.blogspot.com": stripUtopia.StripUtopia,
            "striputopija.blogspot.com": stripUtopia.StripUtopia,
            "www.mangareader.net": mangaReader.MangaReader,
            "mangareader.net": mangaReader.MangaReader,
            "www.readcomicbooksonline.net": readComicBooksOnline.ReadComicBooksOnline,
            "readcomicbooksonline.net": readComicBooksOnline.ReadComicBooksOnline,
            "www.readcomicbooksonline.org": readComicBooksOnline.ReadComicBooksOnline,
            "readcomicbooksonline.org": readComicBooksOnline.ReadComicBooksOnline,
            "www.readcomics.website": readComicsWebsite.ReadComicsWebsite,
            "readcomics.website": readComicsWebsite.ReadComicsWebsite,
            "www.japscan.to": japscan.Japscan,
            "japscan.to": japscan.Japscan,
            "www.hqbr.com.br": hqbr.Hqbr,
            "hqbr.com.br": hqbr.Hqbr,
            "www.comicextra.com": comicextra.ComicExtra,
            "comicextra.com": comicextra.ComicExtra,
            "www.readcomics.io": readComicsIO.ReadComicsIO,
            "readcomics.io": readComicsIO.ReadComicsIO,
            "www.kissmanga.com": None,  # Placeholder for KissManga
            "kissmanga.com": None,       # Placeholder for KissManga
            "www.bato.to": batoto.Batoto,
            "bato.to": batoto.Batoto,
            "manganelo.com": manganelo.Manganelo,
            "mangakakalot.com": manganelo.Manganelo,
            "manganato.com": manganelo.Manganelo,
            "readmanganato.com": manganelo.Manganelo,
            "chapmanganato.com": manganelo.Manganelo,
            "chapmanganato.to": manganelo.Manganelo,
            "www.webtoons.com": webtoons.Webtoons,
            "webtoons.com": webtoons.Webtoons,
            "www.lectortmo.com": lectortmo.LectorTmo,
            "lectortmo.com": lectortmo.LectorTmo,
            "www.mangatoon.mobi": mangatoonMobi.MangatoonMobi,
            "mangatoon.mobi": mangatoonMobi.MangatoonMobi,
            "www.mangadex.org": mangadex.Mangadex,
            "mangadex.org": mangadex.Mangadex,
            "www.qiremanhua.com": quiremanhua.QuireManhua,
            "qiremanhua.com": quiremanhua.QuireManhua,
        }

    def comic_language_resolver(self, language_code):
        language_dict = {
            '0': 'English', '1': 'Italian', '2': 'Spanish', '3': 'French', '4': 'German', 
            '5': 'Portuguese', '6': 'Turkish', '7': 'Indonesian', '8': 'Greek', '9': 'Filipino', 
            '10': 'Polish', '11': 'Thai', '12': 'Malay', '13': 'Hungarian', '14': 'Romanian', 
            '15': 'Arabic', '16': 'Hebrew', '17': 'Russian', '18': 'Vietnamese', '19': 'Dutch', 
            '20': 'Bengali', '21': 'Persian', '22': 'Czech', '23': 'Brazilian', '24': 'Bulgarian', 
            '25': 'Danish', '26': 'Esperanto', '27': 'Swedish', '28': 'Lithuanian', '29': 'Other'
        }
        return language_dict[language_code]

    def checker(self, comic_url, download_directory, chapter_range, **kwargs):
        user_name = kwargs.get("username")
        password = kwargs.get("password")
        current_directory = kwargs.get("current_directory")
        log_flag = kwargs.get("logger")
        sorting = kwargs.get("sorting_order")
        comic_language = kwargs.get("comic_language")
        print_index = kwargs.get("print_index")
        manual_cookies = kwargs.get("cookie")

        if log_flag:
            logging.basicConfig(format='%(levelname)s: %(message)s', filename="Error Log.log", level=logging.DEBUG)
            logging.debug("Comic Url : %s" % comic_url)

        domain = urlparse(comic_url).netloc
        logging.debug("Selected Domain : %s" % domain)

        # Remove trailing "/" to simplify URL checking
        if comic_url.endswith("/"):
            comic_url = comic_url[:-1]

        if domain in self.site_map:
            site_class = self.site_map[domain]
            if site_class:
                site_class(manga_url=comic_url, logger=logging, current_directory=current_directory,
                           sorting_order=sorting, log_flag=log_flag, download_directory=download_directory,
                           chapter_range=chapter_range, conversion=kwargs.get("conversion"),
                           keep_files=kwargs.get("keep_files"),
                           print_index=print_index, manual_cookies=manual_cookies)
            else:
                print("%s is not supported at the moment. You can request it on the Github repository." % domain)
        else:
            print("%s is not supported at the moment. You can request it on the Github repository." % domain)

        return 0
