# @dsanchezseco
import os
import json
from builtins import input


CONFIG_FILE = "config.json"


class ConfigGenerator:
    def __init__(self):
        print("Welcome to the Pull List Config Generator!\n")

        if os.path.isfile(CONFIG_FILE):
            self.handle_existing_config()
        else:
            print("No config file found! Let's create a new one...")
            self.create_config()

    def handle_existing_config(self):
        while True:
            choice = self.display_menu()
            if not choice or choice == "0":
                break
            elif choice == "1":
                self.add_items()
            elif choice == "2":
                self.remove_items()
            elif choice == "3":
                self.edit_config()
            else:
                print("That functionality doesn't exist yet, bye!")
            print("Done!")
            print("May the F=m*a be with you!")

    def display_menu(self):
        print("Previous config found! Do you wanna...")
        print("1. Add new items to pull list?")
        print("2. Remove item from pull list?")
        print("3. Edit config file?")
        print("\n0. Quit")
        choice = input(" >>  ")
        os.system('clear')
        return choice

    def create_config(self):
        data = self.collect_config_data()
        data["comics"] = self.gen_comics_object()
        self.save_config(data)

    def collect_config_data(self):
        data = {}
        data["download_directory"] = self.get_input("download directory (default '<here>/comics')", "comics")
        data["sorting_order"] = self.get_input("sorting order (default 'ascending')", "ascending", ["ascending", "descending"])
        data["conversion"] = self.get_input("conversion (default 'none')", "None", ["cbz", "pdf"])
        data["keep"] = self.get_input("keep images after conversion (default 'True', forced 'True' if no conversion)", "True", ["True", "False"])
        data["image_quality"] = self.get_input("image quality (default 'Best')", "Best", ["Best", "Low"])
        return data

    def get_input(self, prompt, default, options=None):
        while True:
            print(f"{prompt}")
            user_input = input(" >> ")
            if not user_input:
                return default
            if options and user_input not in options:
                print(f"Invalid choice, please choose from {options}")
            else:
                return user_input

    def add_items(self):
        data = self.load_config()
        new_comics = self.gen_comics_object()
        data["comics"].update(new_comics)
        self.save_config(data)

    def edit_config(self):
        data = self.load_config()
        self.edit_config_fields(data)
        self.save_config(data)

    def edit_config_fields(self, data):
        while True:
            options = self.display_edit_options(data)
            choice = input("leave blank to finish >> ")
            if not choice:
                break
            if not choice.isdigit() or int(choice) not in options:
                os.system("clear")
                print("Bad choice, try again!")
                continue
            field = options[int(choice)]
            data[field] = input(f"Editing '{field}': {data[field]} >> ")
            os.system("clear")

    def display_edit_options(self, data):
        print("Select field to edit")
        options = {}
        for index, key in enumerate(data.keys()):
            if key != "comics":
                options[index] = key
                print(f"{index}. {key} (actual value: {data[key]})")
        print()
        return options

    def remove_items(self):
        data = self.load_config()
        comics = data["comics"]
        if not comics:
            print("No comics! Add comics first!")
            return
        self.remove_comic_items(comics)
        data["comics"] = comics
        self.save_config(data)

    def remove_comic_items(self, comics):
        while True:
            options = self.display_comics_options(comics)
            if not options:
                print("No more options, bye!")
                break
            choice = input("leave blank to finish >> ")
            if not choice:
                break
            if not choice.isdigit() or int(choice) not in options:
                os.system("clear")
                print("Bad choice, try again!")
                continue
            del comics[options[int(choice)]]
            os.system("clear")

    def display_comics_options(self, comics):
        print("Select series to remove from pull list")
        options = {}
        for index, (key, value) in enumerate(comics.items()):
            options[index] = key
            print(f"{index}. {key} (next chapter: {value['next']})")
        print()
        return options

    def gen_comics_object(self):
        comics = {}
        while True:
            comic = self.collect_comic_data()
            if not comic["url"]:
                break
            comics[comic["url"]] = comic
            os.system('clear')
        return comics

    def collect_comic_data(self):
        comic = {}
        comic["url"] = input("Series link for comics (leave empty to finish) >> ")
        if not comic["url"]:
            return comic
        comic["next"] = self.get_comic_input("Next chapter to download (default 1)", 1)
        comic["last"] = self.get_comic_input("Last chapter to download (leave blank if download all)", "None")
        comic["username"] = input("Page login username (leave blank if not needed) >> ") or "None"
        comic["password"] = input("Page login password (leave blank if not needed) >> ") or "None"
        comic["comic_language"] = input("Comic language (default 0) >> ") or "0"
        return comic

    def get_comic_input(self, prompt, default):
        value = input(f"{prompt} >> ")
        if not value:
            return default
        return int(value) if value.isdigit() else value

    def load_config(self):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)

    def save_config(self, data):
        with open(CONFIG_FILE, 'w') as file:
            json.dump(data, file, indent=4)


if __name__ == '__main__':
    ConfigGenerator()
