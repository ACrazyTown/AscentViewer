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

import logging
from PyQt5.QtCore import QTimer

# from http://pantburk.info/?blog=77 and https://dzone.com/articles/python-custom-logging-handler-example
class StatusBarHandler(logging.StreamHandler):
    def __init__(self, statusBar, ac):
        '''
        The custom logging handler for the QStatusBar.
        '''
        logging.Handler.__init__(self)
        self.statusBar = statusBar
        self.accentColor = ac

        self.timer = QTimer()

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

if __name__ == "__main__":
    print("This script cannot be used standalone.")
