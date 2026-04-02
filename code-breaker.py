#!/usr/bin/env python3

from dataclasses import dataclass
import os
import random

from readchar import readkey, key
from string import ascii_lowercase
import colorama
from wordlist import words


colorama.init()


def green(s):
    return colorama.Fore.GREEN + s + colorama.Fore.RESET


def red(s):
    return colorama.Fore.RED + s + colorama.Fore.RESET


def yellow(s):
    return colorama.Fore.YELLOW + s + colorama.Fore.RESET


def blue(s):
    return colorama.Fore.BLUE + s + colorama.Fore.RESET


def invert(s):
    return colorama.Back.WHITE + colorama.Fore.BLACK + s + colorama.Style.RESET_ALL


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


@dataclass
class Config:
    rows: int = 5
    showtarget: bool = True
    hints: bool = True


class Menu:
    def __init__(self, config):
        self.config = config
        self.items = []
        self.current = 0
        self.state = None

    def print(self):
        clear()
        for i, item in enumerate(self.items):
            index = i + i
            title = item["title"]
            try:
                value = item["value"]()
                full = f"{index}. {title}: {value}"
            except KeyError:
                value = None
                full = f"{index}. {title}"
            if i == self.current:
                if self.state == "focus":
                    print(f"{index}. {title}: {invert(str(value))}")
                else:
                    print(invert(full))
                continue
            try:
                print(item["style"](full))
            except KeyError:
                print(full)

    def mainloop(self):
        self.print()
        while True:
            k = readkey()
            if self.state == "focus":
                if k == key.LEFT or k == key.RIGHT:
                    self.state = None
                self.items[self.current]["focus"](k)
                self.print()
                continue
            special = None
            if k == key.UP:
                self.current = (self.current - 1) % len(self.items)
            if k == key.DOWN:
                self.current = (self.current + 1) % len(self.items)
            if k == key.RIGHT:
                special = self.items[self.current]["action"]()
            if k == key.LEFT:
                break
            try:
                index = int(k) - 1
                if not (0 <= index < len(self.items)):
                    continue
                self.current = index
                special = self.items[index]["action"]()
            except ValueError:
                pass
            if special == "break":
                break
            self.print()


class TopMenu(Menu):
    def __init__(self, config):
        super().__init__(config)
        self.items = [
            {
                "title": "Start",
                "action": self.onstart,
            },
            {
                "title": "Settings",
                "action": self.onsettings,
            },
            {"title": "Quit", "action": lambda: "break", "style": red},
        ]

    def onstart(self):
        startmenu = StartMenu(self.config)
        startmenu.mainloop()

    def onsettings(self):
        settings = SettingsMenu(self.config)
        settings.mainloop()


class SettingsMenu(Menu):
    def __init__(self, config):
        super().__init__(config)
        self.items = [
            {
                "title": "Rows",
                "action": self.onrows,
                "value": lambda: config.rows,
                "focus": self.withrows,
            },
            {
                "title": "Show target",
                "action": self.onshowtarget,
                "value": lambda: "yes" if config.showtarget else "no",
            },
            {
                "title": "Show hints",
                "action": self.onhints,
                "value": lambda: "yes" if config.hints else "no",
            },
            {"title": "Back", "action": lambda: "break", "style": blue},
        ]

    def onrows(self):
        self.state = "focus"

    def withrows(self, k):
        if k == key.UP:
            self.config.rows = 2 + (self.config.rows - 1) % 8
            return
        if k == key.DOWN:
            self.config.rows = 2 + (self.config.rows - 3) % 8
            return
        try:
            rows = int(k)
            if not (2 <= rows < 10):
                return
            self.config.rows = rows
            self.state = None
        except ValueError:
            pass

    def onshowtarget(self):
        self.config.showtarget = not self.config.showtarget

    def onhints(self):
        self.config.hints = not self.config.hints


class StartMenu(Menu):
    def __init__(self, config):
        super().__init__(config)
        self.items = [
            {
                "title": "Custom",
                "action": self.oncustom,
            },
            {
                "title": "Easy",
                "action": self.oneasy,
            },
            {
                "title": "Hard",
                "action": self.onhard,
            },
            {"title": "Back", "action": lambda: "break", "style": blue},
        ]

    def oncustom(self):
        game = Game(self.config)
        game.mainloop()

    def oneasy(self):
        easyconfig = Config(showtarget=True, hints=True)
        game = Game(easyconfig)
        game.mainloop()

    def onhard(self):
        hardconfig = Config(showtarget=False, hints=False)
        game = Game(hardconfig)
        game.mainloop()


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
                if c == self.target[index] and self.config.hints:
                    formatted.append(blue(c))
                else:
                    formatted.append(c)
            print(self.center(" ".join(formatted)))
        # Player row
        formatted = ""
        for c, d in zip(self.player_row, self.target):
            if c == d:
                formatted += green(c)
            elif self.target.count(c) - self.player_row.count(c) >= 0:
                formatted += yellow(c)
            else:
                formatted += red(c)
            formatted += " "
        formatted = formatted[:-1]
        print(self.center(formatted))
        # Target row
        if self.config.showtarget:
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
            if k == key.LEFT:
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
