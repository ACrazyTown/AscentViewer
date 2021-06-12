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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QHBoxLayout, QMainWindow, QMenuBar, QPushButton, QTabWidget, QToolButton, QVBoxLayout,
                             QWidget)


class MainWindow(QMainWindow):
    def __init__(self, themeLoaderObject):
        themeLoaderObject.printThemeMetadata("AscentedNordDark")

        super().__init__()

        self.setWindowTitle("")
        self.resize(1000, 700)
        self.setFocus()

        # main widgets and layouts
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)

        self.mainTabW = QTabWidget()
        self.mainTabW.setTabsClosable(True)
        self.mainTabW.setMovable(True)

        self.mb = QMenuBar()

        self.fileMenu = self.mb.addMenu("&File")
        self.openImg = self.fileMenu.addAction("&Open image...")
        self.openImg.setShortcut("Ctrl+Q")
        self.fileMenu.addSeparator()
        self.exit = self.fileMenu.addAction("Exit")
        self.exit.setShortcut("Ctrl+Q")

        self.helpMenu = self.mb.addMenu("&Help")
        self.about = self.helpMenu.addAction("About")
        self.about.setShortcut("Shift+F1")

        self.firstButton = QToolButton()
        self.firstButton.setText("File")
        self.firstButton.setFixedHeight(20)
        self.firstButton.setPopupMode(QToolButton.InstantPopup)
        self.firstButton.setMenu(self.fileMenu)

        self.createNewTabButton = QPushButton()
        self.createNewTabButton.setIcon(QIcon("./assets/img/dropdown_arrow.png"))
        self.createNewTabButton.setFixedSize(20, 20)

        cornerWidget = QWidget()

        cornerWidgetLayout = QHBoxLayout(cornerWidget)
        cornerWidgetLayout.setAlignment(Qt.AlignRight)

        self.mainTabW.setCornerWidget(cornerWidget)
        cornerWidgetLayout.addWidget(self.firstButton)
        cornerWidgetLayout.addWidget(self.createNewTabButton)

        mainVBox = QVBoxLayout(mainWidget)
        mainVBox.setContentsMargins(0, 10, 0, 0)
        mainVBox.addWidget(self.mainTabW)

        self.setUpSignalsAndSlots()

    def setUpSignalsAndSlots(self):
        self.mainTabW.tabCloseRequested.connect(lambda index: self.mainTabW.removeTab(index))
        self.createNewTabButton.clicked.connect(lambda: self.mainTabW.addTab(QWidget(), "New Tab"))

    #def crap(self, point):
    #    self.fileMenu.exec_(self.firstButton.mapToGlobal(point))

#    # TODO: FIX MENUBAR WEIRD HOVER ISSUE and fix alt key issue
#    # TODO: fix alt not focusing menu bar
#    # TODO: docs
#    # TODO: fix AltGr issue
#    def keyPressEvent(self, event):
#        if event.isAutoRepeat():
#            return
#        if event.key() == Qt.Key_Alt:
#            #print("Started holding Alt")
#            self.showUnderlines()
#        event.accept()
#
#    def keyReleaseEvent(self, event):
#        if event.isAutoRepeat():
#           return
#        if event.key() == Qt.Key_Alt:
#            #print("Released Alt")
#            self.hideUnderlines()
#        event.accept()
#
#    def focusOutEvent(self, event):
#        # quick alt tab fix
#        self.hideUnderlines()
#        event.accept()
#
#    def showUnderlines(self):
#        self.fileMenu.setTitle("&File")
#        self.openImg.setText("&Open image...")
#        self.exit.setText("&Exit")
#
#        self.helpMenu.setTitle("&Help")
#        self.self.setText("&self")
#
#    def hideUnderlines(self):
#        self.fileMenu.setTitle("File")
#        self.openImg.setText("Open image...")
#        self.exit.setText("Exit")
#
#        self.helpMenu.setTitle("Help")
#        self.self.setText("self")
#
