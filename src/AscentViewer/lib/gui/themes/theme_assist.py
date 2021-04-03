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

from ast import literal_eval

from PyQt5.QtGui import QColor, QPalette
import jstyleson

def set_up_theme(json_manifest, css_qss_stylesheet, json_palette, dict_accentColors):
    """
    Will add text here.
    """

    palette = QPalette()

    palette.setColor(QPalette.Window, QColor(json_palette["palette"]["Window"]))
    palette.setColor(QPalette.WindowText, QColor(json_palette["palette"]["WindowText"]))
    palette.setColor(QPalette.Base, QColor(json_palette["palette"]["Base"]))
    palette.setColor(QPalette.AlternateBase, QColor(json_palette["palette"]["AlternateBase"]))
    palette.setColor(QPalette.ToolTipBase, QColor(json_palette["palette"]["ToolTipBase"]))
    palette.setColor(QPalette.ToolTipText, QColor(json_palette["palette"]["ToolTipText"]))
    palette.setColor(QPalette.Text, QColor(json_palette["palette"]["Text"]))
    palette.setColor(QPalette.Button, QColor(json_palette["palette"]["Button"]))
    palette.setColor(QPalette.ButtonText, QColor(json_palette["palette"]["ButtonText"]))
    palette.setColor(QPalette.BrightText, QColor(json_palette["palette"]["BrightText"]))
    palette.setColor(QPalette.HighlightedText, QColor(json_palette["palette"]["HighlightedText"]))

    palette.setColor(QPalette.Link, QColor(dict_accentColors["accentColorLighter"]))
    palette.setColor(QPalette.Highlight, QColor(dict_accentColors["accentColorMain"]))

    new_stylesheet = css_qss_stylesheet

    new_stylesheet = new_stylesheet.replace("_accentColorMain", dict_accentColors["accentColorMain"])
    new_stylesheet = new_stylesheet.replace("_accentColorDarker", dict_accentColors["accentColorDarker"])
    new_stylesheet = new_stylesheet.replace("_accentColorLighter", dict_accentColors["accentColorLighter"])
    new_stylesheet = new_stylesheet.replace("_accentColorLightest", dict_accentColors["accentColorLightest"])

    style = json_manifest["themeData"]["style"]

    return style, palette, new_stylesheet

if __name__ == "__main__":
    print("This script cannot be used standalone.")
