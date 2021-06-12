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
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget


class ViewerWidget(QWidget):
    def __init__(self, themeLoaderObject):
        super().__init__()

        # main widgets and layouts
        self.pixmap_ = QPixmap("./assets/img/banner.png")

        self.mainPixmapLabel = QLabel()
        self.mainPixmapLabel.setAlignment(Qt.AlignCenter)
        self.mainPixmapLabel.setPixmap(self.pixmap_)
        self.mainPixmapLabel.setMinimumSize(1, 1)

        mainVBox = QVBoxLayout(self)
        mainVBox.setContentsMargins(0, 0, 0, 0)
        mainVBox.addWidget(self.mainPixmapLabel)

    def resizeEvent(self, event):
        self.pixmap = self.pixmap_.scaled(self.geometry().width(), self.geometry().height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.mainPixmapLabel.setPixmap(self.pixmap)
