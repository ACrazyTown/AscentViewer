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

import datetime
import glob
import json
import logging
import os
import platform
import random
import re
import shutil
import signal
import sys
import time

import jstyleson
import pyautogui
from PIL import Image, ImageQt
from PyQt5 import QtCore, QtGui, QtWidgets

import lib.gui.themes.theme_assist as theme_assist

date_format = "%d-%m-%Y %H:%M:%S"
date_format_file = "%d%m%Y_%H%M%S"

class StatusBarHandler(logging.StreamHandler):
    def __init__(self, statusBar, ac):
        '''
        The custom logging handler for the QStatusBar.
        '''
        logging.Handler.__init__(self)
        self.statusBar = statusBar
        self.accentColor = ac

        self.timer = QtCore.QTimer()

    def emit(self, record):
        if record.levelname == "WARNING":
            self.statusBar.setStyleSheet("background: #EBCB8B; color: black;")
        elif record.levelname == "ERROR" or record.levelname == "CRITICAL":
            self.statusBar.setStyleSheet("background: #D08770; color: #181B21;")

        self.statusBar.showMessage(self.format(record), 5000)
        self.timer.timeout.connect(self.timerEnd)

        if self.timer.isActive() == False:
            self.timer.start(5000)

    def timerEnd(self):
        # a temporary solution
        self.statusBar.setStyleSheet(f"background: {self.accentColor};")

    def flush(self):
        pass

class InMemoryLogHandler(logging.StreamHandler):
    def __init__(self):
        global inMemoryLogString, inMemoryLogStringCurrent
        inMemoryLogString = ""
        inMemoryLogStringCurrent = ""
        logging.Handler.__init__(self)

    def emit(self, record):
        global inMemoryLogString, inMemoryLogStringCurrent
        inMemoryLogString += self.format(record)
        inMemoryLogStringCurrent = self.format(record)
        inMemoryLogString += "\n"

    def flush(self):
        pass

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
        self.saveConfigOnExit = True
        sys.excepthook = self.customExceptHook # https://stackoverflow.com/a/33741755/14558305

        # from http://pantburk.info/?blog=77. This code allows the status bar to show warning messages from loggers
        vStatusBarHandler = StatusBarHandler(self.statusBar(), config["theme"]["accentColors"]["accentColorMain"])
        vStatusBarHandler.setLevel(logging.WARN)

        formatter = logging.Formatter("%(levelname)s: %(message)s")
        vStatusBarHandler.setFormatter(formatter)

        ascvLogger.addHandler(vStatusBarHandler)

        # =====================================================
        # gui related stuff:

        ascvLogger.info("Initializing GUI.")
        # from https://stackoverflow.com/questions/27955654/how-to-use-non-standard-custom-font-with-stylesheets
        selawikFonts = glob.glob("data/assets/fonts/selawik/*.ttf")
        for f in selawikFonts:
            f = f.replace("\\", "/")
            QtGui.QFontDatabase.addApplicationFont(f)
        _ = QtGui.QFont("Selawik Bold") # this PROBABLY fixes an issue with KDE Plasma where the font wouldn't display correctly

        if config["hellMode"]: # just a funny easter egg
            mainFont = QtGui.QFont("Selawik")
            mainFont.setBold(True)
            mainFont.setItalic(True)
            mainFont.setPointSize(32)
            QtWidgets.QApplication.setFont(mainFont)
        elif platform.system() == "Windows":
            # Segoe UI is better than the default font, and is included with the latest versions of Windows (starting from Vista(?))
            mainFont = QtGui.QFont("Segoe UI")
            mainFont.setPointSize(9)
            QtWidgets.QApplication.setFont(mainFont)

        self.setWindowTitle(f"AscentViewer")
        self.resize(config["windowProperties"]["width"], config["windowProperties"]["height"])
        self.move(config["windowProperties"]["x"], config["windowProperties"]["y"])
        self.setWindowIcon(QtGui.QIcon("data/assets/img/icon3_small.png"))

        if config["experimental"]["enableExperimentalUI"]:
            # from https://www.geeksforgeeks.org/pyqt5-qlabel-setting-blur-radius-to-the-blur-effect/
            self.blur_effect = QtWidgets.QGraphicsBlurEffect()
            self.blur_effect.setBlurRadius(25)
            # from https://doc.qt.io/qt-5/qgraphicsblureffect.html#blurHints-prop
            self.blur_effect.setBlurHints(QtWidgets.QGraphicsBlurEffect.QualityHint)
            self.blur_effect.setEnabled(False)
            self.setGraphicsEffect(self.blur_effect)

        self.mainWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.mainWidget)

        vBox = QtWidgets.QVBoxLayout(self.mainWidget)
        vBox.setContentsMargins(0, 0, 0, 0)

        self.mainGridFrame = QtWidgets.QFrame()
        self.mainGrid = QtWidgets.QGridLayout(self.mainGridFrame)
        self.mainGrid.setContentsMargins(0, 0, 0, 0)

        vBox.addWidget(self.mainGridFrame)

        self.label = QtWidgets.QLabel()
        self.label.setObjectName("MainImageLabel")
        self.label.setMinimumSize(32, 32)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        mainLabelFont = QtGui.QFont("Selawik", 12)
        self.label.setFont(mainLabelFont)

        self.mainGrid.addWidget(self.label, 0, 0)

        self.mainArrowHBoxFrame = QtWidgets.QFrame()
        mainArrowHBox = QtWidgets.QHBoxLayout(self.mainArrowHBoxFrame)
        mainArrowHBox.setContentsMargins(0, 0, 0, 0)

        leftArrowPixmap = QtGui.QPixmap("data/assets/img/arrow.png")
        leftArrowPixmapIcon = QtGui.QIcon(leftArrowPixmap)

        arrowPixmapSize = leftArrowPixmap.rect().size()

        leftArrowButton = QtWidgets.QPushButton()
        leftArrowButton.setObjectName("arrowButtons")
        leftArrowButton.setFixedSize(75, 185)
        leftArrowButton.setIcon(leftArrowPixmapIcon)
        leftArrowButton.setIconSize(arrowPixmapSize)
        leftArrowButton.clicked.connect(self.prevImage)

        leftArrowVBox = QtWidgets.QVBoxLayout()
        leftArrowVBox.setContentsMargins(0, 0, 0, 0)
        leftArrowVBox.setAlignment(QtCore.Qt.AlignLeft)
        leftArrowVBox.addWidget(leftArrowButton)

        mainArrowHBox.addLayout(leftArrowVBox)


        rightArrowPixmap = leftArrowPixmap.transformed(QtGui.QTransform().scale(-1, 1))
        rightArrowPixmapIcon = QtGui.QIcon(rightArrowPixmap)

        rightArrowButton = QtWidgets.QPushButton()
        rightArrowButton.setObjectName("arrowButtons")
        rightArrowButton.setFixedSize(75, 185)
        rightArrowButton.setIcon(rightArrowPixmapIcon)
        rightArrowButton.setIconSize(arrowPixmapSize)
        rightArrowButton.clicked.connect(self.nextImage)

        rightArrowVBox = QtWidgets.QVBoxLayout()
        rightArrowVBox.setContentsMargins(0, 0, 0, 0)
        rightArrowVBox.setAlignment(QtCore.Qt.AlignRight)
        rightArrowVBox.addWidget(rightArrowButton)

        mainArrowHBox.addLayout(rightArrowVBox)

        # from https://stackoverflow.com/a/29740172/14558305
        with open(f"data/assets/funfacts/funfacts_{lang}.txt", "r", encoding="utf-8") as f:
            funFacts = [x.rstrip() for x in f]

        pickedChoice = random.choice(funFacts)
        with open(f"data/assets/html/{lang}/welcome.html", "r", encoding="utf-8") as f:
            # from https://stackoverflow.com/a/8369345/14558305
            welcome = f.read()
        self.label.setText(f"{welcome}<p>{pickedChoice}</p>")
        # from https://stackoverflow.com/a/37865172/14558305 and https://doc.qt.io/archives/qt-4.8/qlabel.html#linkActivated
        self.label.linkActivated.connect(self.simulateMenuOpen)
        #self.label.linkActivated("https://b").connect(self.openDir)

        mainMenu = self.menuBar()

        fileMenu = mainMenu.addMenu(localization["mainUIElements"]["menuBar"]["file"]["title"])
        navMenu = mainMenu.addMenu(localization["mainUIElements"]["menuBar"]["navigation"]["title"])
        toolsMenu = mainMenu.addMenu(localization["mainUIElements"]["menuBar"]["tools"]["title"])
        if config["debug"]["enableDebugMenu"]:
            debugMenu = mainMenu.addMenu(localization["mainUIElements"]["menuBar"]["debug"]["title"])
        helpMenu = mainMenu.addMenu(localization["mainUIElements"]["menuBar"]["help"]["title"])

        openImgButton = QtWidgets.QAction(QtGui.QIcon("data/assets/img/file.png"), localization["mainUIElements"]["menuBar"]["file"]["openImgText"], self)
        openImgButton.setShortcut("CTRL+O")
        openImgButton.setStatusTip("Open an image file")
        openImgButton.triggered.connect(self.openImage)

        openDirButton = QtWidgets.QAction(QtGui.QIcon("data/assets/img/file.png"), localization["mainUIElements"]["menuBar"]["file"]["openDirText"], self)
        openDirButton.setShortcut("CTRL+Shift+O")
        openDirButton.setStatusTip("Open a directory file")
        openDirButton.triggered.connect(self.openDir)

        exitButton = QtWidgets.QAction(QtGui.QIcon("data/assets/img/door_small.png"), localization["mainUIElements"]["menuBar"]["file"]["exitText"], self)
        exitButton.setShortcut("CTRL+Q")
        exitButton.setStatusTip("Exit application")
        exitButton.triggered.connect(self.close)

        self.navButtonBack = QtWidgets.QAction(localization["mainUIElements"]["menuBar"]["navigation"]["back"], self)
        self.navButtonBack.setShortcut("Left")
        self.navButtonBack.setStatusTip("Go to previous image in directory")
        self.navButtonBack.triggered.connect(self.prevImage)
        self.navButtonBack.setEnabled(False)

        self.navButtonForw = QtWidgets.QAction(localization["mainUIElements"]["menuBar"]["navigation"]["forw"], self)
        self.navButtonForw.setShortcut("Right")
        self.navButtonForw.setStatusTip("Go to next image in directory")
        self.navButtonForw.triggered.connect(self.nextImage)
        self.navButtonForw.setEnabled(False)

        if config["debug"]["enableDebugMenu"]:
            logWindowButton = QtWidgets.QAction("Log Viewer", self)
            logWindowButton.setShortcut("CTRL+Shift+L")
            logWindowButton.setStatusTip("Open the log viewer window.")
            logWindowButton.triggered.connect(self.openLogWin)

            dummyException = QtWidgets.QAction("Raise dummy exception", self)
            dummyException.setShortcut("CTRL+Shift+F10")
            dummyException.setStatusTip("Raise a dummy exception")
            dummyException.triggered.connect(self.dummyExceptionFunc)

        resetCfg = QtWidgets.QAction(localization["mainUIElements"]["menuBar"]["tools"]["resetConfig"], self)
        resetCfg.setShortcut("CTRL+Shift+F9")
        resetCfg.setStatusTip("Reset the configuration file.")
        resetCfg.triggered.connect(self.resetConfigDialog)

        helpButton = QtWidgets.QAction(QtGui.QIcon("data/assets/img/icon3_small.png"), localization["mainUIElements"]["menuBar"]["help"]["help"], self)
        helpButton.setShortcut("F1")
        helpButton.setStatusTip("Open the help window")
        helpButton.triggered.connect(self.openHelpWin)

        aboutButton = QtWidgets.QAction(QtGui.QIcon("data/assets/img/icon3_small.png"), localization["mainUIElements"]["menuBar"]["help"]["about"], self)
        aboutButton.setShortcut("Shift+F1")
        aboutButton.setStatusTip("Open the about window")
        aboutButton.triggered.connect(self.openAboutWin)

        fileMenu.addAction(openImgButton)
        fileMenu.addAction(openDirButton)
        fileMenu.addSeparator()
        fileMenu.addAction(exitButton)

        navMenu.addAction(self.navButtonBack)
        navMenu.addAction(self.navButtonForw)

        if config["debug"]["enableDebugMenu"]:
            debugMenu.addAction(logWindowButton)
            debugMenu.addAction(dummyException)

        toolsMenu.addAction(resetCfg)

        self.copyImage = QtWidgets.QAction("Copy &image (from original source)", self)
        self.copyImage.triggered.connect(self.copyImageFunc)
        self.copyImage.setEnabled(False)

        self.menuBarCompactMenu = QtWidgets.QMenu()

        self.menuBarCompactMenu.addAction(self.copyImage)
        self.menuBarCompactMenu.addSeparator()
        self.menuBarCompactMenu.addMenu(fileMenu)
        self.menuBarCompactMenu.addMenu(navMenu)
        self.menuBarCompactMenu.addMenu(toolsMenu)
        if config["debug"]["enableDebugMenu"]:
            self.menuBarCompactMenu.addMenu(debugMenu)
        self.menuBarCompactMenu.addMenu(helpMenu)

        helpMenu.addAction(helpButton)
        helpMenu.addSeparator()
        helpMenu.addAction(aboutButton)

        self.bottomMenu = QtWidgets.QMenu()

        self.bottomButtonCopyDetails = QtWidgets.QAction("&Copy details", self)
        self.bottomButtonCopyDetails.triggered.connect(self.bottomCopyFunc)
        self.bottomButtonCopyDetails.setEnabled(False)

        self.bottomMenu.addAction(self.copyImage)
        self.bottomMenu.addAction(self.bottomButtonCopyDetails)
        self.bottomMenu.addSeparator()

        bottomButtonSizeMenu = self.bottomMenu.addMenu("Details Panel &size")

        # NOTE: https://stackoverflow.com/a/48501804/14558305
        size90 = QtWidgets.QAction(QtGui.QIcon("data/assets/img/empty_16x16.png"),"&Small (90) (Default)", self)
        size90.triggered.connect(lambda state, h=90: self.bottomChangeSizeFunc(h))

        size130 = QtWidgets.QAction("&Medium-sized (130)", self)
        size130.triggered.connect(lambda state, h=130: self.bottomChangeSizeFunc(h))

        size160 = QtWidgets.QAction("&Large (160)", self)
        size160.triggered.connect(lambda state, h=160: self.bottomChangeSizeFunc(h))

        size200 = QtWidgets.QAction("&Huge (200)", self)
        size200.triggered.connect(lambda state, h=200: self.bottomChangeSizeFunc(h))

        bottomButtonSizeMenu.addActions([size90, size130, size160, size200])

        bottomButton = QtWidgets.QToolButton()
        bottomButton.setObjectName("BottomButton")
        bottomButton.setShortcut("CTRL+ALT+M")
        bottomButton.setMenu(self.bottomMenu)
        bottomButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        bottomButton.setFixedSize(20, 20)

        bottomButtonVBoxFrame = QtWidgets.QFrame()
        bottomButtonVBox = QtWidgets.QVBoxLayout(bottomButtonVBoxFrame)
        bottomButtonVBox.setAlignment(QtCore.Qt.AlignTop) # This probably won't work with PyQt6
        bottomButtonVBox.setContentsMargins(0, 0, 0, 0)
        bottomButtonVBox.addWidget(bottomButton)

        self.bottom = QtWidgets.QFrame()
        self.bottom.setObjectName("Bottom")
        self.bottom.setMinimumHeight(90)
        self.bottom.setMaximumHeight(200)
        self.bottom.setContentsMargins(0, 0, 0, 0)

        btHBox = QtWidgets.QHBoxLayout(self.bottom)

        self.detailsFileIcon = QtWidgets.QLabel()
        self.detailsFileIcon.setFixedSize(60, 60)
        self.detailsFileIcon.setScaledContents(True)
        icon = QtGui.QPixmap("data/assets/img/file.png")
        self.detailsFileIcon.setPixmap(icon)

        self.fileLabel = QtWidgets.QLabel()
        fileLabelFont = QtGui.QFont("Selawik", 14)
        fileLabelFont.setBold(True)
        self.fileLabel.setFont(fileLabelFont)
        self.fileLabel.setText(localization["mainUIElements"]["panelText"])

        self.dateModifiedLabel = QtWidgets.QLabel()

        self.dimensionsLabel = QtWidgets.QLabel()

        self.fileLabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.dateModifiedLabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.dimensionsLabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        btFileInfoVBox1Frame = QtWidgets.QFrame()
        btFileInfoVBox1 = QtWidgets.QVBoxLayout(btFileInfoVBox1Frame)
        btFileInfoVBox1.setContentsMargins(0, 0, 0, 0)
        btFileInfoVBox1.setAlignment(QtCore.Qt.AlignLeft)
        btFileInfoVBox1.addWidget(self.dateModifiedLabel)
        btFileInfoVBox1.addWidget(self.dimensionsLabel)

        btFileInfoContainerHBoxFrame = QtWidgets.QFrame() # A really long name, I know
        btFileInfoContainerHBox = QtWidgets.QHBoxLayout(btFileInfoContainerHBoxFrame)
        btFileInfoContainerHBox.setContentsMargins(0, 0, 0, 0)
        btFileInfoContainerHBox.setAlignment(QtCore.Qt.AlignLeft)
        btFileInfoContainerHBox.addWidget(btFileInfoVBox1Frame)

        btMainVBoxFrame = QtWidgets.QFrame()
        btMainVBox = QtWidgets.QVBoxLayout(btMainVBoxFrame)
        btMainVBox.setAlignment(QtCore.Qt.AlignTop)
        btMainVBox.setContentsMargins(0, 0, 0, 0)
        btMainVBox.addWidget(self.fileLabel)
        btMainVBox.addWidget(btFileInfoContainerHBoxFrame)

        bottomSpacer = QtWidgets.QSpacerItem(10, 0, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)

        btHBox.setAlignment(QtCore.Qt.AlignLeft) # This probably won't work with PyQt6 too
        btHBox.addWidget(self.detailsFileIcon)
        btHBox.addWidget(btMainVBoxFrame)
        btHBox.addItem(bottomSpacer)
        btHBox.addWidget(bottomButtonVBoxFrame)

        if config["experimental"]["enableExperimentalUI"]:
            self.bottomDockWidget = QtWidgets.QDockWidget("Info Panel", self)
            self.bottomDockWidget.setWidget(self.bottom)
            self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.bottomDockWidget)
            vBox.addWidget(self.mainGridFrame)
        else:
            self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
            self.splitter.setObjectName("MainSplitter")
            self.splitter.addWidget(self.mainGridFrame)
            self.splitter.addWidget(self.bottom)
            self.splitter.setCollapsible(0, False)
            self.splitter.setStretchFactor(0, 1)
            self.splitter.setSizes([1, config["windowProperties"]["bottomSplitterPanelH"]])
            vBox.addWidget(self.splitter)

        # from https://stackoverflow.com/a/4839906/14558305
        self.bottom.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.bottom.customContextMenuRequested.connect(self.bottomOnContextMenu)

        self.mainGridFrame.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mainGridFrame.customContextMenuRequested.connect(self.mainGridOnContextMenu)

        # from https://pythonpyqt.com/qtimer/
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateTimerFunc)

        # from https://stackoverflow.com/a/34802367/14558305
        self.label.resizeEvent = (lambda old_method: (lambda event: (self.updateFunction(1), old_method(event))[-1]))(self.label.resizeEvent)

        self.cb = QtWidgets.QApplication.clipboard()

        self.statusBar().showMessage("{} {}".format(localization["mainUIElements"]["statusBar"]["greetMessageBeginning"], ver))

        ascvLogger.info("GUI has been initialized.")

    # from https://stackoverflow.com/a/4839906/14558305
    def bottomOnContextMenu(self, point):
        self.bottomMenu.exec_(self.bottom.mapToGlobal(point))

    def mainGridOnContextMenu(self, point):
        self.menuBarCompactMenu.exec_(self.mainGridFrame.mapToGlobal(point))

    def simulateMenuOpen(self):
        # from https://stackoverflow.com/a/34056847/14558305 and https://pyautogui.readthedocs.io/en/latest/keyboard.html
        # NOTE: only works when the language it set to English (en-us.json)
        pyautogui.hotkey("alt", "f")

    def bottomCopyFunc(self, height):
        details = self.fileLabel.text()
        details += "\n\n"
        details += self.dateModifiedLabel.text()
        details += "\n"
        details += self.dimensionsLabel.text()

        # thanks to https://stackoverflow.com/a/7208922/14558305 and https://stackoverflow.com/a/27086669/14558305
        toReplace = ["<b>", "</b>"]
        for c in toReplace:
            details = details.replace(c, "")

        # thanks to https://stackoverflow.com/a/23119741/14558305
        self.cb.clear(mode=self.cb.Clipboard )
        self.cb.setText(details, mode=self.cb.Clipboard)

    def bottomChangeSizeFunc(self, height):
        self.splitter.setSizes([1, height])

    def copyImageFunc(self):
        self.cb.setImage(QtGui.QImage(self.imgFilePath)) # NOTE: change this

    # the foundation of the code comes from https://stackoverflow.com/a/43570124/14558305
    def updateFunction(self, i):
        '''
        A function that, well, updates. Updates widgets, to be more exact.
        '''

        self.mwWidth = self.label.frameGeometry().width()
        self.mwHeight = self.label.frameGeometry().height()

        if self.imgFilePath != "":
            if i == 0:
                self.im = Image.open(self.imgFilePath)
                self.im = self.im.convert("RGBA") # thanks to https://clay-atlas.com/us/blog/2020/10/31/pyqt5-en-valueerror-unsupported-image-mode-la/

                imWidth, imHeight = self.im.size
                imName = os.path.basename(self.imgFilePath)

                self.im.thumbnail((500, 500))

                dateModified = datetime.datetime.fromtimestamp(os.path.getmtime(self.imgFilePath)).strftime(date_format)
                dimensions = f"{imWidth}x{imHeight}"

                self.fileLabel.setText(imName)
                self.dateModifiedLabel.setText(f"<b>Date modified:</b> {dateModified}")
                self.dimensionsLabel.setText(f"<b>Dimensions:</b> {dimensions}")

                self.setWindowTitle(f"AscentViewer  -  {imName}") # the double spaces are intentional

                self.pixmap_2 = QtGui.QPixmap(self.imgFilePath)

                self.qimagething = ImageQt.ImageQt(self.im)
                self.pixmap_ = QtGui.QPixmap.fromImage(self.qimagething)

                self.updateFunction(1)
            elif i == 1:
                self.timer.stop()
                self.timer.start(250)

                pixmap = self.pixmap_.scaled(self.mwWidth, self.mwHeight, QtCore.Qt.KeepAspectRatio)
                self.label.setPixmap(pixmap)

    def updateTimerFunc(self):
        pixmap = self.pixmap_2.scaled(self.mwWidth, self.mwHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label.setPixmap(pixmap)
        self.timer.stop()

    # I should clean up these two functions below soon
    def openImage(self):
        openImageDialog = QtWidgets.QFileDialog()
        self.imgFilePath, _ = openImageDialog.getOpenFileName(self,
                                                              localization["mainUIElements"]["fileDialogs"]["openImage"]["title"],
                                                              "/",
                                                              "{} (*.jpg *.jpeg *.gif *.png *.bmp)".format(localization["mainUIElements"]["fileDialogs"]["openImage"]["fileTypes"]))

        if self.imgFilePath != "":
            ascvLogger.info(f"Opened image. Image path: \"{self.imgFilePath}\"")
            self.dirPath_ = self.imgFilePath.replace(os.path.basename(self.imgFilePath), "")
            ascvLogger.info(f"Image's directory path: \"{self.dirPath_}\"")

            ascvLogger.debug(f"dirPath: \"{self.dirPath}\", dirPath_: \"{self.dirPath_}\"")

            if self.dirPath != "":
                ascvLogger.debug("dirPath isn't blank")

                if self.dirPath != self.dirPath_:
                    ascvLogger.debug("dirPath and dirPath_ aren't the same, creating new dirImageList, and setting dirPath to dirPath_")
                    self.dirPath = self.dirPath_
                    self.dirMakeImageList(1)
                else:
                    ascvLogger.debug("dirPath and dirPath_ are the same, not creating new dirImageList")
                    self.imageNumber = self.dirImageList.index(self.imgFilePath)
            else:
                ascvLogger.debug("dirPath is blank, creating dirImageList")
                self.dirPath = self.dirPath_
                self.dirMakeImageList(1)
        else:
            ascvLogger.info("imgFilePath is empty!")

    def openDir(self):
        self.dirPath_ = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                                   localization["mainUIElements"]["fileDialogs"]["openDir"]["title"],
                                                                   "/")
        if self.dirPath_ != "":
            ascvLogger.info(f"Successfully opened directory, directory path is: \"{self.dirPath_}\"")

            ascvLogger.debug(f"dirPath: \"{self.dirPath}\", dirPath_: \"{self.dirPath_}\"")

            if self.dirPath != "":
                ascvLogger.debug("dirPath isn't blank")
                if self.dirPath != self.dirPath_:
                    ascvLogger.debug("dirPath and dirPath_ aren't the same, creating new dirImageList, and setting dirPath to dirPath_")
                    self.dirPath = self.dirPath_
                    self.dirMakeImageList(0)
                else:
                    ascvLogger.debug("dirPath and dirPath_ are the same, not creating new dirImageList")
            else:
                ascvLogger.debug("dirPath is blank, creating dirImageList")
                self.dirPath = self.dirPath_
                self.dirMakeImageList(0)
        else:
            ascvLogger.info("dirPath_ is blank!")

    def dirMakeImageList(self, hasOpenedImage):
        fileTypes = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif")
        self.dirImageList_ = []

        for files in fileTypes:
            self.dirImageList_.extend(glob.glob(f"{self.dirPath}/{files}"))

        self.dirImageList_ = [files.replace("\\", "/") for files in self.dirImageList_]
        self.dirImageList_.sort(key=str.lower)

        if len(self.dirImageList_) != 0:
            ascvLogger.info(f"Successfully created dirImageList_. It's not empty.")
            ascvLogger.debug(f"dirImageList_: {self.dirImageList_}")
            ascvLogger.info(f"dirImageList_ length: {len(self.dirImageList_)}")
            ascvLogger.info(f"Setting dirImageList to dirImageList_")

            self.dirImageList = self.dirImageList_

            if hasOpenedImage == 1:
                self.imageNumber = self.dirImageList.index(self.imgFilePath)
            else:
                self.imageNumber = 0

            self.imgFilePath = self.dirImageList[self.imageNumber]

            self.mainGrid.addWidget(self.mainArrowHBoxFrame, 0, 0)
            self.navButtonBack.setEnabled(True)
            self.navButtonForw.setEnabled(True)
            self.copyImage.setEnabled(True)
            self.bottomButtonCopyDetails.setEnabled(True)
            self.updateFunction(0)
        else:
            ascvLogger.info(f"Successfully created dirImageList_, but it's empty! Not setting dirImageList to dirImageList_")

    # I should clean up these two too
    def prevImage(self):
        ascvLogger.debug(f"Showing previous image, imageNumber = {self.imageNumber}")
        if self.imageNumber != 0:
            self.imageNumber -= 1
        else:
            self.imageNumber = len(self.dirImageList) - 1

        self.imgFilePath = self.dirImageList[self.imageNumber]
        self.updateFunction(0)

    def nextImage(self):
        ascvLogger.debug(f"Showing next image, imageNumber = {self.imageNumber}")
        if self.imageNumber != len(self.dirImageList) - 1:
            self.imageNumber += 1
        else:
            self.imageNumber = 0

        self.imgFilePath = self.dirImageList[self.imageNumber]
        self.updateFunction(0)

    def dumpJson(self):
        toWrite = json.dumps(config, ensure_ascii=False, indent=4)

        # from https://stackoverflow.com/questions/46746537/json-force-every-opening-curly-brace-to-appear-in-a-new-separate-line
        toWrite = re.sub(r'^((\s*)".*?":)\s*([\[{])', r'\1\n\2\3', toWrite, flags=re.MULTILINE)

        toWrite += "\n" # https://codeyarns.com/tech/2017-02-22-python-json-dump-misses-last-newline.html

        with open("data/user/config.json", "w", encoding="utf-8", newline="\n") as cf:
            # from https://stackoverflow.com/questions/5214578/print-string-to-text-file
            cf.write(toWrite)

    def onCloseActions(self):
        config["windowProperties"]["width"] = self.width()
        config["windowProperties"]["height"] = self.height()
        config["windowProperties"]["x"] = self.x()
        config["windowProperties"]["y"] = self.y()
        config["windowProperties"]["bottomSplitterPanelH"] = self.bottom.height()

        if self.saveConfigOnExit == True:
            self.dumpJson()

    def closeEvent(self, event):
        if config["prompts"]["enableExitPrompt"]:
            if config["experimental"]["enableExperimentalUI"]:
                self.blur_effect.setEnabled(True)

            reply = QtWidgets.QMessageBox(self)
            reply.setWindowTitle(localization["mainUIElements"]["exitDialog"]["title"])
            reply.setText("<b>{}</b>".format(localization["mainUIElements"]["exitDialog"]["mainText"]))
            reply.setInformativeText("<i>{}</i>".format(localization["mainUIElements"]["exitDialog"]["informativeText"]))

            # from https://stackoverflow.com/a/35889474/14558305
            reply.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            buttonY = reply.button(QtWidgets.QMessageBox.Yes)
            buttonY.setText(localization["mainUIElements"]["commonQMessageBoxStrings"]["yes"])
            buttonN = reply.button(QtWidgets.QMessageBox.No)
            buttonN.setText(localization["mainUIElements"]["commonQMessageBoxStrings"]["no"])

            checkbox = QtWidgets.QCheckBox(localization["mainUIElements"]["commonQMessageBoxStrings"]["doNotShowAgain"])
            icon = QtGui.QPixmap("data/assets/img/door_small.png")
            reply.setIconPixmap(QtGui.QPixmap(icon))
            reply.setCheckBox(checkbox)
            reply.setModal(True)

            x = reply.exec_()

            if checkbox.isChecked():
                ascvLogger.info("Disabling prompt...")
                config["prompts"]["enableExitPrompt"] = False
            else:
                ascvLogger.info("Not disabling prompt.")

            if x == QtWidgets.QMessageBox.Yes:
                ascvLogger.info("Exiting...")
                self.onCloseActions()
                event.accept()
            else:
                ascvLogger.info("Not exiting.")
                if config["experimental"]["enableExperimentalUI"]:
                    self.blur_effect.setEnabled(False)
                event.ignore()

        else:
            ascvLogger.info("Exit prompt is disabled, exiting...")
            self.onCloseActions()
            event.accept()

    def resetConfigDialog(self):
        '''
        A function that shows a dialog that asks the user if they want to reset the configuration file
        (copy config.json from default_config to the user folder). If they respond with "Yes", the function
        resets the configuration to its defaults.
        '''
        if config["experimental"]["enableExperimentalUI"]:
            self.blur_effect.setEnabled(True)

        reply = QtWidgets.QMessageBox(self)
        reply.setWindowTitle(localization["mainUIElements"]["resetConfigDialog"]["title"])
        reply.setText("<b>{}</b>".format(localization["mainUIElements"]["resetConfigDialog"]["mainText"]))
        reply.setInformativeText("<i>{}</i>".format(localization["mainUIElements"]["resetConfigDialog"]["informativeText"]))

        # from https://stackoverflow.com/a/35889474/14558305
        reply.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        buttonY = reply.button(QtWidgets.QMessageBox.Yes)
        buttonY.setText(localization["mainUIElements"]["commonQMessageBoxStrings"]["yes"])
        buttonN = reply.button(QtWidgets.QMessageBox.No)
        buttonN.setText(localization["mainUIElements"]["commonQMessageBoxStrings"]["no"])

        checkbox = QtWidgets.QCheckBox(localization["mainUIElements"]["resetConfigDialog"]["checkboxText"])
        icon = QtGui.QPixmap("data/assets/img/icon3_small.png")
        reply.setIconPixmap(QtGui.QPixmap(icon))
        reply.setCheckBox(checkbox)
        reply.setModal(True)

        x = reply.exec_()

        if checkbox.isChecked():
            config["prompts"]["enableExitPrompt"] = False
            self.onCloseActions()
            self.close()

        if x == QtWidgets.QMessageBox.Yes:
            shutil.copyfile("data/assets/default_config/config.json", "data/user/config.json")
            self.saveConfigOnExit = False
        else:
            if config["experimental"]["enableExperimentalUI"]:
                self.blur_effect.setEnabled(False)

    # from https://stackoverflow.com/a/33741755/14558305
    def customExceptHook(self, exctype, exception, traceback):
        ascvLogger.critical(f"An exception occurred: \"{exception}\" | Saving settings in case of a fatal issue...")
        sys.__excepthook__(exctype, exception, traceback)
        self.onCloseActions()

    def dummyExceptionFunc(self):
        raise Exception("Dummy exception!")

    def openSettingsWin(self):
        settings = QtWidgets.QDialog(self, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        settings.resize(700, 500)
        geo = settings.geometry()
        geo.moveCenter(self.geometry().center())
        settings.setGeometry(geo)

        settings.setAttribute(QtCore.Qt.WA_QuitOnClose, True)
        settings.setModal(True)
        settings.setWindowTitle("Settings")

        settings.show()

    def openLogWin(self):
        # not using a modal QDialog (like the About window) here because I want this window to be non-modal
        logViewer = QtWidgets.QMainWindow(self, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        logViewer.resize(600, 400)
        geo = logViewer.geometry()
        geo.moveCenter(self.geometry().center())
        logViewer.setGeometry(geo)

        logViewer.setWindowTitle("Log Viewer")
        logViewer.setAttribute(QtCore.Qt.WA_QuitOnClose, True) # https://stackoverflow.com/questions/16468584/qwidget-doesnt-close-when-main-window-is-closed

        label = QtWidgets.QLabel("AscentViewer's Log Viewer")
        font = QtGui.QFont("Selawik", 14)
        font.setBold(True)
        label.setFont(font)

        if platform.system() == "Windows":
            monospaceFont = QtGui.QFont("Consolas", 10)
        else:
            monospaceFont = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)

        self.logTextEdit = QtWidgets.QPlainTextEdit(logViewer)
        self.logTextEdit.setFont(monospaceFont)

        self.logViewerCheckbox = QtWidgets.QCheckBox("Read-only")
        self.logViewerCheckbox.setChecked(True)
        # thanks to https://stackoverflow.com/a/36289772/14558305 for making me realize it's "toggled" and not "clicked"
        self.logViewerCheckbox.toggled.connect(self.logTextEditChangeMode)

        self.logTextEditChangeMode()
        self.logTextEditRefresh()

        spacer = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)

        copyButton = QtWidgets.QPushButton("Copy")
        copyButton.clicked.connect(self.logTextEditCopy)

        refreshButton = QtWidgets.QPushButton("Refresh")
        refreshButton.clicked.connect(self.logTextEditRefresh)

        clearButton = QtWidgets.QPushButton("Clear")
        clearButton.clicked.connect(self.logTextEditClear)

        buttonHBoxFrame = QtWidgets.QFrame()
        buttonHBox = QtWidgets.QHBoxLayout(buttonHBoxFrame)
        buttonHBox.setContentsMargins(0, 0, 0, 0)
        buttonHBox.addWidget(self.logViewerCheckbox)
        buttonHBox.addItem(spacer)
        buttonHBox.addWidget(copyButton)
        buttonHBox.addWidget(refreshButton)
        buttonHBox.addWidget(clearButton)

        mainVBoxFrame = QtWidgets.QFrame()
        logViewer.setCentralWidget(mainVBoxFrame)
        mainVBox = QtWidgets.QVBoxLayout(mainVBoxFrame)
        mainVBox.setAlignment(QtCore.Qt.AlignLeft)
        mainVBox.addWidget(label)
        mainVBox.addWidget(self.logTextEdit)
        mainVBox.addWidget(buttonHBoxFrame)

        logViewer.show()

    def logTextEditChangeMode(self):
        if self.logViewerCheckbox.isChecked():
            self.logTextEdit.setReadOnly(True)
        else:
            self.logTextEdit.setReadOnly(False)

    def logTextEditClear(self):
        self.logTextEdit.clear()

    def logTextEditRefresh(self):
        self.logTextEdit.setPlainText(inMemoryLogString)

    def logTextEditCopy(self):
        self.logTextEdit.selectAll()
        self.logTextEdit.copy()

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
        font = QtGui.QFont("Selawik", 26)
        font.setBold(True)
        programName.setFont(font)

        helpTitle = QtWidgets.QLabel("Help")
        helpTitle.setObjectName("HelpTitle")
        font = QtGui.QFont("Selawik Semilight", 26)
        helpTitle.setFont(font)

        spacer = QtWidgets.QSpacerItem(2, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)

        # thanks to https://stackoverflow.com/a/35861477/14558305
        textView = QtWidgets.QTextBrowser()

        # from https://stackoverflow.com/a/8369345/14558305
        with open(f"data/assets/html/{lang}/help.html", "r", encoding="utf-8") as f:
            data = f.read()

        textView.setOpenExternalLinks(True)
        textView.setText(data)

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

        # from https://stackoverflow.com/a/8369345/14558305
        with open(f"data/assets/html/{lang}/help.html", "r", encoding="utf-8") as f:
            data = f.read()

        textView.setText(data)

        helpWin.exec_()

    def openAboutWin(self):
        about.__init__(self, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        about.setLayout(about.gridLayout)
        about.resize(900, 502)

        _translate = QtCore.QCoreApplication.translate
        about.setWindowTitle(_translate("Form", localization["mainUIElements"]["aboutWindow"]["title"]))
        about.programName.setText(_translate("Form", "AscentViewer"))
        about.majorReleaseName.setText(_translate("Form", "Cobalt"))
        about.versionLabel.setText(_translate("Form", localization["mainUIElements"]["aboutWindow"]["mainVersion"]))
        about.version.setText(_translate("Form", ver))
        about.label.setText(_translate("Form", localization["mainUIElements"]["aboutWindow"]["PyVersion"]))
        try:
            about.label_9.setText(_translate("Form", platform.python_version()))
        except:
            about.label_9.setText(_translate("Form", "unknown"))
        about.label_2.setText(_translate("Form", localization["mainUIElements"]["aboutWindow"]["PyQtVersion"]))
        try:
            # from https://wiki.python.org/moin/PyQt/Getting%20the%20version%20numbers%20of%20Qt%2C%20SIP%20and%20PyQt
            about.label_10.setText(_translate("Form", QtCore.PYQT_VERSION_STR))
        except:
            about.label_10.setText(_translate("Form", "unknown"))
        # from https://stackoverflow.com/a/8369345/14558305
        with open(f"data/assets/html/{lang}/about.html", "r") as f:
            desc = f.read()
        about.label_11.setText(_translate("Form", desc))
        about.label_4.setText(_translate("Form", "<a href=\"https://github.com/despawnedd/AscentViewer/\">{}</a>").format(localization["mainUIElements"]["aboutWindow"]["GitHubLink"])) # thanks to Anthony for .format
        about.label_6.setText(_translate("Form", "<a href=\"https://dd.acrazytown.com/AscentViewer/\">{}</a>").format(localization["mainUIElements"]["aboutWindow"]["website"]))

        about.exec_()

# from https://stackoverflow.com/a/31688396/14558305 and https://stackoverflow.com/a/39215961/14558305
class StreamToLogger:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass

if __name__ == "__main__":
    # apparently makes CTRL + C work properly in console ("https://stackoverflow.com/questions/5160577/ctrl-c-doesnt-work-with-pyqt")
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        os.chdir(__file__.replace(os.path.basename(__file__), "")) # thanks to Anthony for this
    except:
        pass

    with open("manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)
    ver = manifest["version"]

    userDirPath = "data/user"
    if os.path.isdir(userDirPath) != True:
        os.mkdir(userDirPath)

    tempDirPath = "data/user/temp/"
    if os.path.isdir(tempDirPath) != True:
        os.mkdir(tempDirPath)

    logDirPath = "data/user/temp/logs"
    if os.path.isdir(logDirPath) != True:
        os.mkdir(logDirPath)

    configPath = "data/user/config.json"
    if os.path.isfile(configPath) != True:
        shutil.copyfile("data/assets/default_config/config.json", "data/user/config.json")

    config = json.load(open(configPath, "r", encoding="utf-8")) # using json instead of QSettings, for now
    lang = config["localization"]["lang"]
    localization = json.load(open(f"data/assets/localization/lang/{lang}.json", "r", encoding="utf-8"))

    # If this causes issues, disable deleting logs on startup.
    print("Deleting logs on statup is ", end="")
    if config["temporary_files"]["logs"]["deleteLogsOnStartup"]:
        print("enabled, erasing all logs...")
        logs = glob.glob("data/user/temp/logs/log*.log")
        for f in logs:
            os.remove(f)
    else:
        print("disabled, not deleting logs.")

    logfile = f"data/user/temp/logs/log_{datetime.datetime.now().strftime(date_format_file)}.log"

    mainFormatterString = "[%(asctime)s | %(name)s | %(funcName)s | %(levelname)s] %(message)s"
    mainFormatter = logging.Formatter(mainFormatterString, date_format)

    # thanks to Jan and several other sources for this
    loggingLevel = getattr(logging, config["debug"]["logging"]["loggingLevel"])
    logging.basicConfig(level=loggingLevel,
                        handlers=[logging.StreamHandler(), logging.FileHandler(logfile, "a", "utf-8")],
                        format=mainFormatterString,
                        datefmt=date_format)

    ascvLogger = logging.getLogger("Main logger")
    stderrLogger = logging.getLogger("stderr logger")
    if sys.executable.endswith("pythonw.exe") != True:
        sys.stderr = StreamToLogger(stderrLogger, logging.ERROR)

    # from http://pantburk.info/?blog=77
    vInMemoryLogHandler = InMemoryLogHandler()
    vInMemoryLogHandler.setLevel(getattr(logging, config["debug"]["logging"]["loggingLevel"]))
    vInMemoryLogHandler.setFormatter(mainFormatter)

    ascvLogger.addHandler(vInMemoryLogHandler)

    logIntroLine = "="*20 + "[ BEGIN LOG ]" + "="*20
    with open(logfile, "a") as f: # this code is a bit messy but all this does is just write the same thing both to the console and the logfile
        f.write(f"{logIntroLine}\n")
    print(logIntroLine)

    ascvLogger.info(f"Arguments: {sys.argv}")

    if platform.system() == "Windows":
        # makes the AscentViewer icon appear in the taskbar, more info here: "https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105"
        # (newer command gotten from 15-minute-apps: "https://github.com/learnpyqt/15-minute-apps")
        from PyQt5 import QtWinExtras
        QtWinExtras.QtWin.setCurrentProcessExplicitAppUserModelID(f"DespawnedDiamond.AscentViewer.ascv.{ver}")

    if platform.system() == "Linux":
        # just a fun little piece of code that prints out your distro name and version
        import distro
        distroName = " ".join(distro.linux_distribution()).title()
        ascvLogger.info(f"The OS is {platform.system()} ({distroName}).")
    else:
        ascvLogger.info(f"The OS is {platform.system()}.")

    app = QtWidgets.QApplication(sys.argv)

    with open("data/assets/themes/{}/manifest.json".format(config["theme"]["name"]), "r", encoding="utf-8") as f:
        manifest = jstyleson.load(f)

    with open("data/assets/themes/{}/{}".format(config["theme"]["name"], manifest["themeData"]["paletteJSONLocation"]), "r", encoding="utf-8") as f:
        palette_json = jstyleson.load(f)

    with open("data/assets/themes/{}/{}".format(config["theme"]["name"], manifest["themeData"]["styleSheetLocation"]), "r", encoding="utf-8") as f:
        old_stylesheet = f.read()

    # not naming things the same as in the theme_assist script to prevent confusion
    style, palette, new_stylesheet = theme_assist.set_up_theme(manifest, old_stylesheet, palette_json, config["theme"]["accentColors"])

    app.setStyle(style)
    app.setPalette(palette)
    app.setStyleSheet(new_stylesheet)

    from lib.gui.other_windows.about import *

    # start the actual program
    window = MainUi()
    window.show()

    sys.exit(app.exec_())
