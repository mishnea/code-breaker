#!/usr/bin/env python3

from dataclasses import dataclass
import os
import random

from readchar import readkey, key
from string import ascii_lowercase
import colorama
from wordlist import words


colorama.init()


def good(s):
    return colorama.Fore.GREEN + s + colorama.Fore.RESET


def bad(s):
    return colorama.Fore.RED + s + colorama.Fore.RESET


def info(s):
    return colorama.Fore.BLUE + s + colorama.Fore.RESET


def invert(s):
    return colorama.Back.WHITE + colorama.Fore.BLACK + s + colorama.Style.RESET_ALL


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


class Menu:
    def __init__(self, config):
        self.config = config
        self.items = []
        self.current = 0

    def print(self):
        clear()
        for i, item in enumerate(self.items):
            title = f"{i}. {item['title']}"
            if item["value"]:
                title += f": {item["value"]()}"
            if i == self.current:
                print(invert(title))
            else:
                print(title)

    def mainloop(self):
        self.print()
        while True:
            k = readkey()
            if k == key.UP:
                self.current = (self.current - 1) % len(self.items)
            if k == key.DOWN:
                self.current = (self.current + 1) % len(self.items)
            if k == key.RIGHT:
                self.items[self.current]["action"]()
            try:
                index = int(k)
                if index >= len(self.items):
                    continue
                self.current = index
                self.items[index]["action"]()
            except ValueError:
                pass
            self.print()


class TopMenu(Menu):
    def __init__(self, config):
        super().__init__(config)
        self.items = [
            {"title": "Start", "action": self.onstart, "value": None},
            {"title": "Settings", "action": self.onsettings, "value": None},
        ]

    def onstart(self):
        game = Game(self.config)
        game.mainloop()

    def onsettings(self):
        settings = SettingsMenu(self.config)
        settings.mainloop()


class SettingsMenu(Menu):
    def __init__(self, config):
        super().__init__(config)
        self.items = [
            {
                "title": "Show target",
                "action": self.onshowtarget,
                "value": lambda: "yes" if config.showtarget else "no",
            },
            {
                "title": "Show colours",
                "action": self.oncolors,
                "value": lambda: "yes" if config.colors else "no",
            },
        ]

    def onshowtarget(self):
        self.config.showtarget = not self.config.showtarget

    def oncolors(self):
        self.config.colors = not self.config.colors


@dataclass
class Config:
    rows: int = 5
    showtarget: bool = True
    colors: bool = True


class Game:
    def __init__(self, config):
        self.config = config
        self.target = random.choice(words)
        self.width = 21
        weights = [1 + self.target.count(c) for c in ascii_lowercase]
        self.player_row = random.choices(ascii_lowercase, weights, k=len(self.target))
        self.random_rows = [self.genrow() for _ in range(config.rows)]
        self.attempts = 0

    @property
    def remaining_chars(self):
        return [
            target_c
            for player_c, target_c in zip(self.player_row, self.target)
            if player_c != target_c
        ]

    def genrow(self):
        weights = [1 + self.remaining_chars.count(c) for c in ascii_lowercase]
        return "".join(
            random.choices(ascii_lowercase, weights, k=1)[0]
            for _ in range(len(self.target))
        )

    def center(self, s, char=" "):
        pad_length = int((self.width + 1) / 2 - len(self.target))
        pad = char * pad_length
        return pad + s + pad

    def print(self):
        clear()
        # Score row
        print(invert(f"Attempts: {self.attempts}".center(self.width)))
        # Scrambled rows
        for row in self.random_rows[::-1]:
            formatted = []
            for index, c in enumerate(row):
                if c == self.target[index]:
                    formatted.append(info(c))
                else:
                    formatted.append(c)
            print(self.center(" ".join(formatted)))
        # Player row
        formatted = " ".join(
            good(c) if c == d else bad(c) for c, d in zip(self.player_row, self.target)
        )
        print(self.center(formatted))
        # Target row
        print(invert(" ".join(list(self.target)).center(self.width)))

    def replace(self, r):
        if r == "\n" or r == " ":
            self.player_row = list(self.random_rows[0])
            return True
        replaced = False
        for i, (c, d) in enumerate(zip(self.player_row, self.random_rows[0])):
            if c == r:
                replaced = True
                self.player_row[i] = d
        return replaced

    def shift(self):
        self.random_rows = self.random_rows[1:]
        self.random_rows.append(self.genrow())

    def mainloop(self):
        self.print()
        while True:
            k = readkey()
            if k == key.UP:
                break
            replaced = self.replace(k)
            if not replaced:
                continue
            self.shift()
            self.attempts += 1
            self.print()
            if "".join(self.player_row) == "".join(self.target):
                print("You wonnered")
                break


if __name__ == "__main__":
    config = Config()
    menu = TopMenu(config)
    menu.mainloop()
