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


class SettingsWidget(QWidget):
    def __init__(self, themeLoaderObject):
        super().__init__()

        # main widgets and layouts
        self.background = QLabel(self)
        self.background.setPixmap(QPixmap("./assets/img/settingsbg_alpha4.png"))
        self.background.setAlignment(Qt.AlignBottom | Qt.AlignRight)

        mainVBox = QVBoxLayout(self)
        mainVBox.setContentsMargins(0, 0, 0, 0)

    def resizeEvent(self, event):
        self.background.resize(self.geometry().size())
