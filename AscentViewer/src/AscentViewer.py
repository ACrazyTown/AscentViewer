# AscentViewer, a Python image viewer.
# Copyright (C) 2020-2021 DespawnedDiamond, A Crazy Town and other contributors
#
# This file is part of AscentViewer.
#
# AscentViewer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AscentViewer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with AscentViewer.  If not, see <https://www.gnu.org/licenses/>.

# =====================================================
# Thank you for using and/or checking out AscentViewer!
# =====================================================

'''
A simple launcher for AscentViewer. Sort of based on "https://github.com/qutebrowser/qutebrowser/blob/master/qutebrowser/__main__.py"
'''

import sys
import os
import subprocess
import py_compile
import argparse

try:
    os.chdir(__file__.replace(os.path.basename(__file__), ""))
except:
    pass

# from https://stackoverflow.com/a/6598286/14558305
def customExceptHook(exctype, value, traceback):
    if exctype == KeyboardInterrupt:
        print("\nKeyboardInterrupt occurred.")
    else:
        sys.__excepthook__(exctype, value, traceback)
sys.excepthook = customExceptHook

# FIX USAGE!
parser = argparse.ArgumentParser(
    description="This is the AscentViewer launcher script.",
    epilog="Thanks for using AscentViewer!",
    conflict_handler="resolve")

parser.add_argument("-V", "--version", help="show program version", action="store_true")
parser.add_argument("-m", "--minimal", help="open the minimal AscentViewer instead of the main one", action="store_true")

args = parser.parse_args()

if args.version:
    with open("AscentViewer_files/data/assets/version_info.txt", "r") as f:
        ver = f.read().replace("\n", "")

    print(f"AscentViewer version : {ver}")
    parser.exit()

if args.minimal:
    pyLocation = "AscentViewer_files/ascv_minimal.py"
    pycLocation = "AscentViewer_files/ascv_minimal.pyc"
else:
    pyLocation = "AscentViewer_files/ascv_main.py"
    pycLocation = "AscentViewer_files/ascv_main.pyc"

print("Compiling AscentViewer...")
py_compile.compile(pyLocation, pycLocation) # from https://stackoverflow.com/a/5607315/14558305

print(f"Python is located at {sys.executable}") # from https://stackoverflow.com/a/2589722/14558305
print("Starting AscentViewer...\n")
subprocess.run([sys.executable, pyLocation])
