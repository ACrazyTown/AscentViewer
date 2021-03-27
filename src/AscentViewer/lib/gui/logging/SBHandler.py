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
