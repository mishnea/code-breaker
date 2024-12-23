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


def invert(s):
    return colorama.Back.WHITE + colorama.Fore.BLACK + s + colorama.Style.RESET_ALL


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


class Game:
    def __init__(self, rows):
        self.word = random.choice(words)
        self.width = 20
        weights = [1 + self.word.count(c) for c in ascii_lowercase]
        self.bottom_row = random.choices(ascii_lowercase, weights, k=len(self.word))
        self.matrix = [self.genrow() for _ in range(rows)]
        self.attempts = 0

    @property
    def remaining(self):
        return [d for c, d in zip(self.bottom_row, self.word) if c != d]
    
    def genrow(self):
        weights = [1 + self.remaining.count(c) for c in ascii_lowercase]
        return random.choices(ascii_lowercase, weights, k=len(self.word))

    def print(self):
        clear()
        # Score row
        print(invert(f"Attempts: {self.attempts}".center(self.width)))
        # Scrambled rows
        print(
            *(" ".join(row).center(self.width) for row in self.matrix[::-1]),
            sep="\n",
        )
        # Player row
        formatted = " ".join(
            good(c) if c == d else bad(c) for c, d in zip(self.bottom_row, self.word)
        )
        print(formatted.center(len(formatted) - 2 * len(self.bottom_row) + self.width))
        # Target row
        print(invert(" ".join(list(self.word)).center(self.width)))

    def replace(self, r):
        replaced = False
        for i, (c, d) in enumerate(zip(self.bottom_row, self.matrix[0])):
            if c == r:
                replaced = True
                self.bottom_row[i] = d
        return replaced

    def shift(self):
        self.matrix = self.matrix[1:]
        self.matrix.append(self.genrow())

    def start(self):
        while True:
            self.print()
            c = readchar()
            if c == "\x1b":
                # escape pressed
                break
            replaced = self.replace(c)
            if not replaced:
                continue
            self.shift()
            self.attempts += 1
            if "".join(self.bottom_row) == "".join(self.word):
                self.print()
                print("You wonnered")
                break


if __name__ == "__main__":
    game = Game(5)
    game.start()
