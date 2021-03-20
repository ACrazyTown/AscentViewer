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

import sys
import os
import platform
import signal
import glob
import shutil
import datetime

from PyQt5 import QtGui, QtCore, QtWidgets

ver = "1.0.0_dev-1.0"

date_format = "%d-%m-%Y %H:%M:%S"
date_format_file = "%d%m%Y_%H%M%S" # for log files

class MainUi(QtWidgets.QMainWindow):
    def __init__(self):
        '''
        The core AscentViewer function. It sets up the UI, as well as some other things.
        '''
        super().__init__()

        # =====================================================
        # non-gui related stuff:

        self.dirPath = ""
        self.imgFilePath = ""
        sys.excepthook = self.except_hook # from https://stackoverflow.com/a/33741755/14558305

        # =====================================================
        # gui related stuff:

        if platform.system() == "Windows":
            # Segoe UI is better than the default font, and is included with the latest versions of Windows (starting from Vista(?))
            mainFont = QtGui.QFont("Segoe UI")
            mainFont.setPointSize(9)
            QtWidgets.QApplication.setFont(mainFont)

        self.setWindowTitle(f"Minimal AscentViewer")
        self.resize(800, 700)

        self.mainWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.mainWidget)

        vBox = QtWidgets.QVBoxLayout(self.mainWidget)
        vBox.setContentsMargins(0, 0, 0, 0)

        self.label = QtWidgets.QLabel()
        self.label.setText("<h1>Welcome to AscentViewer!</h1><p>Open an image or a folder to get started.</p>")
        self.label.setMinimumSize(16, 16)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        mainLabelFont = QtGui.QFont()
        mainLabelFont.setPointSize(12)
        self.label.setFont(mainLabelFont)

        mainMenu = self.menuBar()

        fileMenu = mainMenu.addMenu("&File")
        navMenu = mainMenu.addMenu("&Navigation")
        helpMenu = mainMenu.addMenu("&Help")

        openImgButton = QtWidgets.QAction("&Open image...", self)
        openImgButton.setShortcut("CTRL+O")
        openImgButton.setStatusTip("Open an image file")
        openImgButton.triggered.connect(self.openImage)

        openDirButton = QtWidgets.QAction("Open &folder...", self)
        openDirButton.setShortcut("CTRL+Shift+O")
        openDirButton.setStatusTip("Open a directory file")
        openDirButton.triggered.connect(self.openDir)

        exitButton = QtWidgets.QAction("&Exit", self)
        exitButton.setShortcut("CTRL+Q")
        exitButton.setStatusTip("Exit application")
        exitButton.triggered.connect(self.close)

        self.navButtonBack = QtWidgets.QAction("&Previous image", self)
        self.navButtonBack.setShortcut("Left")
        self.navButtonBack.setStatusTip("Go to previous image in directory")
        self.navButtonBack.triggered.connect(self.prevImage)
        self.navButtonBack.setEnabled(False)

        self.navButtonForw = QtWidgets.QAction("&Next image", self)
        self.navButtonForw.setShortcut("Right")
        self.navButtonForw.setStatusTip("Go to next image in directory")
        self.navButtonForw.triggered.connect(self.nextImage)
        self.navButtonForw.setEnabled(False)

        helpButton = QtWidgets.QAction("&Help", self)
        helpButton.setShortcut("F1")
        helpButton.setStatusTip("Open the help window")
        helpButton.triggered.connect(self.openHelpWin)

        aboutButton = QtWidgets.QAction("&About", self)
        aboutButton.setShortcut("Shift+F1")
        aboutButton.setStatusTip("Open the about window")
        aboutButton.triggered.connect(self.openAboutWin)
        aboutButton.setEnabled(False)

        fileMenu.addAction(openImgButton)
        fileMenu.addAction(openDirButton)
        fileMenu.addSeparator()
        fileMenu.addAction(exitButton)

        navMenu.addAction(self.navButtonBack)
        navMenu.addAction(self.navButtonForw)

        self.menuBarCompactMenu = QtWidgets.QMenu()
        self.menuBarCompactMenu.addMenu(fileMenu)
        self.menuBarCompactMenu.addMenu(navMenu)
        self.menuBarCompactMenu.addMenu(helpMenu)

        helpMenu.addAction(helpButton)
        helpMenu.addSeparator()
        helpMenu.addAction(aboutButton)

        vBox.addWidget(self.label)

        # from https://stackoverflow.com/a/4839906/14558305
        self.label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.label.customContextMenuRequested.connect(self.labelOnContextMenu)

        # from https://pythonpyqt.com/qtimer/
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateTimerFunc)

        # from https://stackoverflow.com/a/34802367/14558305
        self.label.resizeEvent = (lambda old_method: (lambda event: (self.updateFunction(1), old_method(event))[-1]))(self.label.resizeEvent)

        self.statusBar().showMessage("Successfully loaded, version: {ver}")

    # from https://stackoverflow.com/a/4839906/14558305
    def labelOnContextMenu(self, point):
        self.menuBarCompactMenu.exec_(self.label.mapToGlobal(point))

    # the foundation of the code comes from https://stackoverflow.com/a/43570124/14558305
    def updateFunction(self, i):
        '''
        A function that, well, updates. Updates widgets, to be more exact.
        '''

        self.mwWidth = self.label.frameGeometry().width()
        self.mwHeight = self.label.frameGeometry().height()

        if self.imgFilePath != "":
            if i == 0:
                # i == 0: set up things, update image to high quality image
                pixmap_ = QtGui.QPixmap(self.imgFilePath)
                pixmap = pixmap_.scaled(self.mwWidth, self.mwHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.label.setPixmap(pixmap)
            elif i == 1:
                # i == 1: low quality resize
                if self.timer.isActive() == False:
                    self.timer.start(250)

                pixmap_ = QtGui.QPixmap(self.imgFilePath)
                pixmap = pixmap_.scaled(self.mwWidth, self.mwHeight, QtCore.Qt.KeepAspectRatio)
                self.label.setPixmap(pixmap)

    def updateTimerFunc(self):
        pixmap_ = QtGui.QPixmap(self.imgFilePath)
        pixmap = pixmap_.scaled(self.mwWidth, self.mwHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label.setPixmap(pixmap)
        self.timer.stop()

    # I should clean up these two functions below soon
    def openImage(self):
        openImageDialog = QtWidgets.QFileDialog()
        self.imgFilePath, _ = openImageDialog.getOpenFileName(self,
                                                              "Select an image that you want to open...",
                                                              "/",
                                                              "Image files (*.jpg *.jpeg *.gif *.png *.bmp)")

        if self.imgFilePath != "":
            self.dirPath_ = self.imgFilePath.replace(os.path.basename(self.imgFilePath), "")

            if self.dirPath != "":
                if self.dirPath != self.dirPath_:
                    self.dirPath = self.dirPath_
                    self.dirMakeImageList(1)
                else:
                    self.imageNumber = self.dirImageList.index(self.imgFilePath)
            else:
                self.dirPath = self.dirPath_
                self.dirMakeImageList(1)

    def openDir(self):
        self.dirPath_ = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                                   "Select a folder that you want to open...",
                                                                   "/")
        if self.dirPath_ != "":
            if self.dirPath != "":
                if self.dirPath != self.dirPath_:
                    self.dirPath = self.dirPath_
                    self.dirMakeImageList(0)
            else:
                self.dirPath = self.dirPath_
                self.dirMakeImageList(0)

    def dirMakeImageList(self, hasOpenedImage):
        fileTypes = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif")
        self.dirImageList_ = []

        for files in fileTypes:
            self.dirImageList_.extend(glob.glob(f"{self.dirPath}/{files}"))

        self.dirImageList_ = [files.replace("\\", "/") for files in self.dirImageList_]
        self.dirImageList_.sort(key=str.lower)

        if len(self.dirImageList_) != 0:
            self.dirImageList = self.dirImageList_

            if hasOpenedImage == 1:
                self.imageNumber = self.dirImageList.index(self.imgFilePath)
            else:
                self.imageNumber = 0

            self.imgFilePath = self.dirImageList[self.imageNumber]

            self.updateFunction(0)
            self.navButtonBack.setEnabled(True)
            self.navButtonForw.setEnabled(True)

    # I should clean up these two too
    def prevImage(self):
        if self.imageNumber != 0:
            self.imageNumber -= 1
        else:
            self.imageNumber = len(self.dirImageList) - 1

        self.imgFilePath = self.dirImageList[self.imageNumber]
        self.updateFunction(0)

    def nextImage(self):
        if self.imageNumber != len(self.dirImageList) - 1:
            self.imageNumber += 1
        else:
            self.imageNumber = 0

        self.imgFilePath = self.dirImageList[self.imageNumber]
        self.updateFunction(0)

    # from https://stackoverflow.com/a/33741755/14558305
    def except_hook(self, cls, exception, traceback):
        # custom except hook
        sys.__excepthook__(cls, exception, traceback)
        self.onCloseActions()

    def openHelpWin(self):
        helpWin = QtWidgets.QDialog(self, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        helpWin.resize(400, 600)
        geo = helpWin.geometry()
        geo.moveCenter(self.geometry().center())
        helpWin.setGeometry(geo)

        helpWin.setAttribute(QtCore.Qt.WA_QuitOnClose, True)
        helpWin.setModal(True)
        helpWin.setWindowTitle("Help")

        icon = QtWidgets.QLabel()
        icon.setPixmap(QtGui.QPixmap("data/assets/img/icon3_small64.png"))

        # from the about window
        programName = QtWidgets.QLabel("AscentViewer")
        font = QtGui.QFont()
        font.setPointSize(26)
        font.setBold(True)
        programName.setFont(font)

        helpTitle = QtWidgets.QLabel("Help")
        font = QtGui.QFont()
        font.setPointSize(26)
        helpTitle.setFont(font)
        #helpTitle.setStyleSheet("color: rgba(0, 0, 0, 0.5);") # from https://www.w3schools.com/cssref/css3_pr_opacity.asp

        spacer = QtWidgets.QSpacerItem(2, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)

        # thanks to https://stackoverflow.com/a/35861477/14558305
        textView = QtWidgets.QTextBrowser()

        helpText = """
        <h1>Help</h1>
        <p>You can read the AscentViewer documentation <a href="https://github.com/despawnedd/AscentViewer/wiki"><b>here</b></a>.</p>
        """
        textView.setText(helpText)

        headerHBoxFrame = QtWidgets.QFrame()
        headerHBox = QtWidgets.QHBoxLayout(headerHBoxFrame)
        headerHBox.setContentsMargins(0, 0, 0, 0)
        headerHBox.setAlignment(QtCore.Qt.AlignLeft)
        headerHBox.addWidget(icon)
        headerHBox.addWidget(programName)
        headerHBox.addItem(spacer)
        headerHBox.addWidget(helpTitle)

        mainVBoxLayout = QtWidgets.QVBoxLayout(helpWin)
        mainVBoxLayout.addWidget(headerHBoxFrame)
        mainVBoxLayout.addWidget(textView)
        mainVBoxLayout.setAlignment(QtCore.Qt.AlignTop)

        helpWin.show()

    def openAboutWin(self):
        about = QtWidgets.QDialog(self, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

if __name__ == "__main__":
    # apparently makes CTRL + C work properly in console ("https://stackoverflow.com/questions/5160577/ctrl-c-doesnt-work-with-pyqt")
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        os.chdir(__file__.replace(os.path.basename(__file__), "")) # thanks to Anthony for this
    except:
        pass

    # start the actual program
    app = QtWidgets.QApplication(sys.argv)

    window = MainUi()
    window.show()

    sys.exit(app.exec_())
