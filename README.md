# Code Breaker

## Gameplay

Your aim is to create the target word, written at the bottom with a white background.

Your current line is 2nd from the bottom, with characters in green and red, representing whether they are correct.

Each turn, you must press a letter on your keyboard that exists in your current line, in order to replace that letter with the one in the line above.

If there are multiple instances of that letter in your line, they will all be replaced.

## Install

`git clone https://github.com/mishnea/code-breaker.git`

`cd code-breaker`

`python -m venv .venv`

Windows: `.\.venv\Script\Activate.ps1`

Linux: `source .venv/bin/activate`

`pip install -r requirements.txt`

`python code-breaker.py`
