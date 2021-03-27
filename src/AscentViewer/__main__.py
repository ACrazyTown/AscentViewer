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
A simple launcher for AscentViewer. Sort of based on https://github.com/qutebrowser/qutebrowser/blob/master/qutebrowser/__main__.py and https://stackoverflow.com/questions/4042905/what-is-main-py
'''

import argparse
import json
import os
import py_compile
import subprocess
import sys
import tkinter
import tkinter.messagebox

try:
    os.chdir(__file__.replace(os.path.basename(__file__), ""))
except:
    pass

# from https://stackoverflow.com/a/6598286/14558305
def customExceptHook(exctype, exception, traceback):
    if exctype == KeyboardInterrupt:
        print("\nKeyboardInterrupt occurred.")
    else:
        sys.__excepthook__(exctype, exception, traceback)
        root = tkinter.Tk()
        root.overrideredirect(1)
        root.withdraw()
        tkinter.messagebox.showerror("Exception", exception)

sys.excepthook = customExceptHook

# NOTE: finish the "usage" argument
parser = argparse.ArgumentParser(
    description="This is the AscentViewer launcher script.",
    epilog="Thanks for using AscentViewer!",
    conflict_handler="resolve")

parser.add_argument("-V", "--version", help="show program version", action="store_true")
parser.add_argument("-m", "--minimal", help="open the minimal AscentViewer instead of the main one", action="store_true")

args = parser.parse_args()

if args.version:
    with open("manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)
        ver = manifest["version"]

    print(f"AscentViewer version: {ver}")
    parser.exit()

pyLocation = "ascv_"

if args.minimal:
    pyLocation += "minimal"
else:
    pyLocation += "main"

pyLocation += ".py"

pycLocation = pyLocation + "c"

print("Compiling AscentViewer...")
py_compile.compile(pyLocation, pycLocation) # from https://stackoverflow.com/a/5607315/14558305

print(f"Python is located at {sys.executable}") # from https://stackoverflow.com/a/2589722/14558305
print("Starting AscentViewer...\n")
subprocess.run([sys.executable, pyLocation])
