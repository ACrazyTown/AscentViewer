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

# TODO: maybe clean up the code a bit

import jstyleson
import os
from glob import glob
from pprint import pprint

from PyQt5.QtGui import QColor, QPalette

class ThemeLoader:
    def __init__(self, themeLocation):
        """Init function. Sets up the themes located in themeLocation."""

        self.validThemes = []

        self.globThing = glob(os.path.join(themeLocation, "*", ""))

        for x in self.globThing:
            if os.path.isfile(x + "manifest.json"):
                with open(x + "manifest.json", "r", encoding="utf-8") as f:
                    manifest = jstyleson.load(f)

                if os.path.isfile(x + manifest["themeData"]["paletteJSONPath"]) and os.path.isfile(x + manifest["themeData"]["styleSheetPath"]):
                    self.validThemes.append({"name": manifest["commonMetadata"]["name"], "path": x, "manifest": manifest})

    def applyTheme(self, themeName, accentColor, QApplicationInstance):
        """The function that, as the name says, applies the theme (specified by themeName)"""
        print(f"The selected theme ({themeName}) ", end="")
        try:
            themeDict = next(item for item in self.validThemes if item["name"] == themeName)
            with open(themeDict["path"] + themeDict["manifest"]["themeData"]["paletteJSONPath"], "r", encoding="utf-8") as f:
                paletteJSON = jstyleson.load(f)

            QApplicationInstance.setStyle(themeDict["manifest"]["themeData"]["style"])
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(paletteJSON["palette"]["Window"]))
            palette.setColor(QPalette.WindowText, QColor(paletteJSON["palette"]["WindowText"]))
            palette.setColor(QPalette.Base, QColor(paletteJSON["palette"]["Base"]))
            palette.setColor(QPalette.AlternateBase, QColor(paletteJSON["palette"]["AlternateBase"]))
            palette.setColor(QPalette.ToolTipBase, QColor(paletteJSON["palette"]["ToolTipBase"]))
            palette.setColor(QPalette.ToolTipText, QColor(paletteJSON["palette"]["ToolTipText"]))
            palette.setColor(QPalette.Text, QColor(paletteJSON["palette"]["Text"]))
            palette.setColor(QPalette.Button, QColor(paletteJSON["palette"]["Button"]))
            palette.setColor(QPalette.ButtonText, QColor(paletteJSON["palette"]["ButtonText"]))
            palette.setColor(QPalette.BrightText, QColor(paletteJSON["palette"]["BrightText"]))
            palette.setColor(QPalette.HighlightedText, QColor(paletteJSON["palette"]["HighlightedText"]))

            palette.setColor(QPalette.Link, QColor(accentColor))
            palette.setColor(QPalette.Highlight, QColor(accentColor))

            QApplicationInstance.setPalette(palette)

            with open(themeDict["path"] + themeDict["manifest"]["themeData"]["styleSheetPath"], "r", encoding="utf-8") as f:
                QApplicationInstance.setStyleSheet(f.read())

            print("has been applied.")
        except:
            print("could not be applied. Please check if the theme is valid.")

    def printThemeMetadata(self, themeName):
        """The function prints out the theme's (specified by themeName) metadata."""
        try:
            themeDict = next(item for item in self.validThemes if item["name"] == themeName)
            print("Theme metadata\n=====================================================")
            print(f'Name: "{themeDict["manifest"]["commonMetadata"]["name"]}"')
            print(f'Description: "{themeDict["manifest"]["commonMetadata"]["description"]}"')
            print(f'Author: "{themeDict["manifest"]["commonMetadata"]["author"]}"')
            print(f'Version: "{themeDict["manifest"]["commonMetadata"]["version"]}"')
        except:
            print("[!] Something went wrong with printing the theme info. Please check if the theme is valid.")

    def getThemeIconPackPath(self, themeName):
        try:
            themeDict = next(item for item in self.validThemes if item["name"] == themeName)
            return themeDict["manifest"]["themeData"]["imgPackPath"]
        except:
            pass
