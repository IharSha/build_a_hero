import pickle
import os

from text_helpers import print_input_options, input_line
from character import Character


class Game:
    data = {}

    def __init__(self, name):
        self.name = name
        self.file_name = f"{name}.dat"
        self.character = None

    def start_game(self):
        if os.path.exists(self.file_name):
            self.load()
        else:
            self.create_character()

    def create_character(self):
        name = input_line("Name your character")
        self.data["character"] = Character(name)
        self.save()

        return self.character

    def load_character(self):
        self.character = self.data["character"]
        print(f"Happy to see you again, {self.character.name}!")

        return self.character

    def save(self):
        with open(self.file_name, "wb") as f:
            return pickle.dump(self.data, f)

    def load(self):
        try:
            with open(self.file_name, "rb") as f:
                self.data = pickle.load(f)
        except IOError:
            pass

        return self.data

    def __show_raw_data(self):
        print("Saved data:", str(self.data), "\n")

    def __update_data(self, key, value):
        self.data[key] = value


def start():
    print("\nWelcome to the world!\nIf you want to quit type `q` on any input.")
    username = input_line("Enter the name of your old game or type a new one:")
    game = Game(username)
    game.start_game()
    character = game.load_character()

    options = {
        "upgrade": ("1", "Level up"),
        "show": ("2", "Show character"),
        "exit": ("0", "Exit"),
    }
    while True:
        print_input_options(options)
        ans = input_line()
        if ans == options["upgrade"][0]:
            character.upgrade()
            game.save()
            print(f"Congrats! now you're level {character.level}.")
            print(character.stats)
        elif ans == options["show"][0]:
            print(character)
        elif ans == options["exit"][0]:
            print("Bye!")
            break


start()
