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
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QFont, QKeySequence, QPixmap
from PyQt5.QtWidgets import (QDesktopWidget, QFrame, QGridLayout, QHBoxLayout, QLabel,
                             QProgressBar, QShortcut, QVBoxLayout, QWidget)

class Splash(QWidget):
    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.setWindowTitle("AscentViewer splash screen")
        self.setFixedSize(700, 500)
        self.setCursor(Qt.WaitCursor)
        self.setAttribute(Qt.WA_TranslucentBackground)
        #self.setWindowOpacity(.99)

        # main widgets and layouts
        mainFrame = QFrame(self)
        mainFrame.setFixedSize(700, 500)

        mainGrid = QGridLayout(mainFrame)
        mainGrid.setContentsMargins(0, 0, 0, 0)

        background = QLabel()
        background.setPixmap(QPixmap("./assets/img/splash_bg3ws.png"))

        cancel = QLabel("Ctrl+Q or Alt+F4 to cancel")
        #cancel.setFixedHeight(30)
        cancel.setStyleSheet("""
                            QLabel
                            {
                                border:none;
                                background: rgba(0, 0, 0, 0);
                            }
                            """)

        font = QFont("Selawik", 36)
        font.setBold(True)
        topLabel = QLabel("AscentViewer")
        topLabel.setFont(font)

        version = QLabel("version 1.0.0")
        version.setAlignment(Qt.AlignBottom)
        version.setFixedHeight(30)
        version.setFont(QFont("Selawik Light", 20))
        version.setStyleSheet("color: #8FBCBB;")

        loadingLabel = QLabel("Loading...")
        loadingLabel.setAlignment(Qt.AlignBottom)
        loadingLabel.setFont(QFont("Segoe UI", 12))
        loadingLabel.setFixedHeight(40)

        self.progBar = QProgressBar()
        self.progBar.setValue(0)

        mainGrid.addWidget(background, 0, 0)

        mainVBox = QVBoxLayout()
        mainVBox.setContentsMargins(70, 70, 70, 70)

        top = QHBoxLayout()
        top.setAlignment(Qt.AlignTop | Qt.AlignRight)
        top.setContentsMargins(0, 0, 0, 0)
        top.addWidget(cancel)

        bottom = QVBoxLayout()
        bottom.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.addWidget(topLabel)
        bottom.addWidget(version)
        bottom.addWidget(loadingLabel)
        bottom.addWidget(self.progBar)

        mainVBox.addLayout(top)
        mainVBox.addLayout(bottom)

        mainGrid.addLayout(mainVBox, 0, 0)

        # from https://stackoverflow.com/questions/37718329/pyqt5-draggable-frameless-window
        self.center()
        self.oldPos = self.pos()

        self.shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut.activated.connect(quit)

    # these three functions are from https://stackoverflow.com/questions/37718329/pyqt5-draggable-frameless-window
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

if __name__ == "__main__":
    print("This script cannot be run standalone.")
    quit() # probably unnecessary but eh
#else:
#    from .ui import * # https://stackoverflow.com/questions/4142151/how-to-import-the-class-within-the-same-directory-or-sub-directory
