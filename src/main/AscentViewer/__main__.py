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

# importing all the necessary libraries
import os
import sys
from platform import system
from signal import SIG_DFL, SIGINT, signal

from PyQt5.QtGui import QFont  # may not be necessary
from PyQt5.QtWidgets import QApplication

from lib.ui.tab_widgets.about import *
from lib.ui.tab_widgets.settings import *
from lib.ui.tab_widgets.viewer import *
from lib.ui.tab_widgets.welcome import *
from lib.ui.themes.theme_loader import *
from lib.ui.win.main import *
from lib.ui.win.splash import *


# localize subclass
class Localize():
    def __init__(self):
        self.tr_MainWindow()

    def tr_MainWindow(self):
        """
        self.setWindowTitle("AscentViewer")
        self.fileMenu = self.mb.addMenu("File")
        self.openImg = self.fileMenu.addAction("&Open image...")
        self.openImg.setShortcut("Ctrl+Q")
        self.fileMenu.addSeparator()
        self.exit = self.fileMenu.addAction("Exit")
        self.exit.setShortcut("Ctrl+Q")

        self.helpMenu = self.mb.addMenu("Help")
        self.about = self.helpMenu.addAction("about")
        self.about.setShortcut("Shift+F1")
        self.createNewTabButton.clicked.connect(lambda: self.mainTabW.addTab(QWidget(), ""))
        """
        mainWin.setWindowTitle(app.translate("Window Title", "AscentViewer"))

        #mainWin.fileMenu.setTitle((app.translate("File Menu Title", "&File")))

def openViewerTab(self):
    mainWin.mainTabW.addTab(viewer, "Image Viewer")
    mainWin.mainTabW.setCurrentWidget(viewer)

def openSettingsTab(self):
    mainWin.mainTabW.addTab(settings, "Settings")
    mainWin.mainTabW.setCurrentWidget(settings)

def doShit():
    mainWin.mainTabW.addTab(welcome, "Welcome")
    welcome.openImageLink.linkActivated.connect(openViewerTab)
    welcome.settingsLink.linkActivated.connect(openSettingsTab)

if __name__ == "__main__":
    app = QApplication(sys.argv) #+ ["-platform windows:darkmode=1 altgr"]) # https://forum.qt.io/topic/101391/windows-10-dark-theme/10

    signal(SIGINT, SIG_DFL)

    try:
        os.chdir(__file__.replace(os.path.basename(__file__), ""))
    except:
        pass

    if system() == "Windows":
        app.setFont(QFont("Segoe UI", 9)) # 8 maybe

    mainThemeLoader = ThemeLoader("./assets/themes/")
    mainThemeLoader.applyTheme("AscentedNordDark", "#AFB7C6", app) #777cc1
    iconPath = mainThemeLoader.getThemeIconPackPath("AscentedNordDark")

    splash = Splash()
    mainWin = MainWindow(mainThemeLoader)
    about = AboutWin()
    welcome = WelcomeWidget(mainThemeLoader)
    viewer = ViewerWidget(mainThemeLoader)
    settings = SettingsWidget(mainThemeLoader)

    mainWin.show()

    doShit()
    Localize()

    sys.exit(app.exec_())
