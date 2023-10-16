#!/usr/bin/env python3
from src.select_run_mode import select_run_mode
from src.select_run_mode import run_mode
from src.exceptions import RequiredSelection

from dotenv import load_dotenv
from dotenv import find_dotenv
load_dotenv(find_dotenv())


def work():
    try:
        mode_name = select_run_mode()
        run_mode(mode_name)
    except RequiredSelection as e:
        print(e)


if __name__ == '__main__':
    work()
