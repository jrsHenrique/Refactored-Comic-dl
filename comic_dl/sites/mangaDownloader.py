class MangaDownloader:
    def __init__(self, manga_url, download_directory, chapter_range, **kwargs):
        self.manga_url = manga_url
        self.download_directory = download_directory
        self.chapter_range = chapter_range
        self.user_credentials = {
            "username": kwargs.get("username"),
            "password": kwargs.get("password")
        }
        self.comic_language = kwargs.get("comic_language")
        self.current_directory = kwargs.get("current_directory")
        self.conversion = kwargs.get("conversion")
        self.keep_files = kwargs.get("keep_files")
        self.logging = kwargs.get("log_flag")
        self.sorting = kwargs.get("sorting_order")
        self.print_index = kwargs.get("print_index")
        self.comic_name = self.name_cleaner(manga_url)

    def name_cleaner(self, url):
        raise NotImplementedError

    def download_chapter(self, comic_url):
        raise NotImplementedError

    def download_series(self):
        raise NotImplementedError

    def user_login(self):
        raise NotImplementedError