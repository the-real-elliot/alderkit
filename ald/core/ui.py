#!/usr/bin/env python3

import shutil

WIDTH = shutil.get_terminal_size().columns

def banner():
    print("\033[1;31m")
    print(r"""
     █████╗ ██╗     ██████╗
    ██╔══██╗██║     ██╔══██╗
    ███████║██║     ██║  ██║
    ██╔══██║██║     ██║  ██║
    ██║  ██║███████╗██████╔╝
    ╚═╝  ╚═╝╚══════╝╚═════╝

        A L D  //  E L L I O T
        Security Operations Core
    """)
    print("\033[0m")

def info(text):
    print(f"\033[1;33m[ALD]\033[0m {text}")

def good(text):
    print(f"\033[1;32m[+]\033[0m {text}")

def bad(text):
    print(f"\033[1;31m[-]\033[0m {text}")
