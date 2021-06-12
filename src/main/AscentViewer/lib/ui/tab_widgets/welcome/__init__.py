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
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (QLabel, QSizePolicy, QSpacerItem, QVBoxLayout,
                             QWidget)


class WelcomeWidget(QWidget):
    def __init__(self, themeLoaderObject):
        super().__init__()

        # main widgets and layouts
        self.background = QLabel(self)
        self.background.setPixmap(QPixmap("./assets/img/pcbg_alpha.png"))
        self.background.setAlignment(Qt.AlignBottom | Qt.AlignRight)

        titleFont = QFont("Selawik", 28)
        subtitleFont = QFont("Selawik Semilight", 14)
        labelFont = QFont("Selawik", 11)

        title = QLabel("Welcome (back) to <b>hell</b>")
        title.setFont(titleFont)
        title.setMinimumSize(1, 1)

        subtitle = QLabel("Here are some things you can do:")
        subtitle.setFont(subtitleFont)
        subtitle.setMinimumSize(1, 1)

        self.openImageLink = QLabel('<a href="https://">Open an image</a>')
        self.openImageLink.setFont(labelFont)
        self.openImageLink.setMinimumSize(1, 1)

        self.openFolderLink = QLabel('<a href="https://">Open an folder</a>')
        self.openFolderLink.setFont(labelFont)
        self.openFolderLink.setMinimumSize(1, 1)

        self.settingsLink = QLabel('<a href="https://">Open the settings</a>')
        self.settingsLink.setFont(labelFont)
        self.settingsLink.setMinimumSize(1, 1)

        mainVBox = QVBoxLayout(self)
        mainVBox.setAlignment(Qt.AlignTop)
        mainVBox.setContentsMargins(50, 70, 50, 50)
        mainVBox.addWidget(title)
        mainVBox.addWidget(subtitle)
        mainVBox.addSpacerItem(QSpacerItem(1, 20, QSizePolicy.Fixed))
        mainVBox.addWidget(self.openImageLink)
        mainVBox.addWidget(self.openFolderLink)
        mainVBox.addWidget(self.settingsLink)

    def resizeEvent(self, event):
        self.background.resize(self.geometry().size())
