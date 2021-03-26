import logging

# from http://pantburk.info/?blog=77 and https://dzone.com/articles/python-custom-logging-handler-example
class StatusBarHandler(logging.StreamHandler):
    def __init__(self, statusBar):
        '''
        The custom logging handler for the QStatusBar.
        '''
        logging.Handler.__init__(self)
        self.statusBar = statusBar

    def emit(self, record):
        self.statusBar.showMessage(self.format(record))

        if record.levelname == "WARNING":
            self.statusBar.setStyleSheet("background: #EBCB8B; color: black;")
        elif record.levelname == "ERROR":
            self.statusBar.setStyleSheet("background: #D08770; color: black;")
        elif record.levelname == "CRITICAL":
            self.statusBar.setStyleSheet("background: #BF616A;")

    def flush(self):
        pass
