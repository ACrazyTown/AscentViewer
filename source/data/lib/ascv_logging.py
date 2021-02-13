import sys
import logging
import datetime
import json

# from https://stackoverflow.com/a/31688396/14558305, https://stackoverflow.com/a/39215961/14558305
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

config = json.load(open("data/user/config.json", encoding="utf-8"))

date_format_file = "%d%m%Y_%H%M%S"
date_format = "%d/%m/%Y %H:%M:%S"

logfile = f"data/user/temp/logs/log_{datetime.datetime.now().strftime(date_format_file)}.log"
loggingLevel = getattr(logging, config["debug"]["logging"]["loggingLevel"])

# thanks to Jan and several other sources for this
logging.basicConfig(level=loggingLevel,
                    handlers=[logging.StreamHandler(), logging.FileHandler(logfile, "w", "utf-8")],
                    format="[%(asctime)s | %(name)s | %(funcName)s | %(levelname)s] %(message)s",
                    datefmt=date_format)

ascvLogger = logging.getLogger("Main logger")
stdouterrLogger = logging.getLogger("stdout/stderr")
sys.stdout = StreamToLogger(stdouterrLogger, logging.INFO)
sys.stderr = StreamToLogger(stdouterrLogger, logging.ERROR)

print("="*20 + "[ BEGIN LOG ]" + "="*20)
#if os.path.exists(logfile):
#    with open(logfile, "w") as f:
#        f.write(f"{m}\n")
#        print(m)