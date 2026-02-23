#!/usr/bin/env python3

from readchar import readchar
import os
import random
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


class Game:
    def __init__(self, rows):
        self.target = random.choice(words)
        self.width = 21
        weights = [1 + self.target.count(c) for c in ascii_lowercase]
        self.player_row = random.choices(ascii_lowercase, weights, k=len(self.target))
        self.random_rows = [self.genrow() for _ in range(rows)]
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

    def start(self):
        self.print()
        while True:
            c = readchar()
            if c == "\x1b":
                # escape pressed
                break
            replaced = self.replace(c)
            if not replaced:
                continue
            self.shift()
            self.attempts += 1
            self.print()
            if "".join(self.player_row) == "".join(self.target):
                print("You wonnered")
                break


if __name__ == "__main__":
    game = Game(5)
    game.start()
