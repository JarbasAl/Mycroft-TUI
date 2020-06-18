import io
import os
import time
from threading import Thread, Lock
from unidecode import unidecode


def remove_non_ascii(text):
    return unidecode(text)


##############################################################################
# Log file monitoring
log_lock = Lock()
max_log_lines = 10000
mergedLog = []
logs = {}
log_files = []


class LogMonitorThread(Thread):
    def __init__(self, filename, logid):
        global log_files, logs
        Thread.__init__(self)
        self.filename = filename
        self.st_results = os.stat(filename)
        self.logid = str(logid)
        log_files.append(filename)
        if filename not in logs:
            logs[self.logid] = []

    def run(self):
        while True:
            try:
                st_results = os.stat(self.filename)
                # Check if file has been modified since last read
                if not st_results.st_mtime == self.st_results.st_mtime:
                    self.read_file_from(self.st_results.st_size)

                    self.st_results = st_results
            except OSError as e:
                # ignore any file IO exceptions, just try again
                pass
            except Exception as e:
                print(e)
            time.sleep(1)

    def read_file_from(self, bytefrom):
        global logs
        global log_lock
        global mergedLog

        with io.open(self.filename) as fh:
            fh.seek(bytefrom)
            while True:
                line = fh.readline()
                line = remove_non_ascii(line)
                if line == "":
                    break

                with log_lock:
                    try:
                        _, level, _, name, msg = line.split("|")
                    except:
                        level = "DEBUG"
                        msg = line
                        name = "print"
                    if "werkzeug" in name:
                        msg = msg.replace("- -", "-")
                    clean = self.logid + " | ".join([level.strip(),
                                                     name.strip(),
                                                     msg.strip()])
                    if clean in logs[self.logid]:
                        # suppress duplicates
                        logs[self.logid].remove(clean)
                    if clean in mergedLog:
                        mergedLog.remove(clean)
                    mergedLog.append(clean)
                    logs[self.logid].append(clean)

        # Limit log to  max_log_lines
        if len(mergedLog) >= max_log_lines:
            with log_lock:
                cToDel = len(mergedLog) - max_log_lines
                for l in mergedLog[:cToDel]:
                    logid = l.split(" | ")[0]
                    logs[logid].remove(l)
                del mergedLog[:cToDel]


def start_log_monitor(filename):
    if os.path.isfile(filename):
        name = os.path.basename(filename).split(".")[0] + " | "
        thread = LogMonitorThread(filename, name)
        thread.setDaemon(True)  # this thread won't prevent prog from exiting
        thread.start()
        return thread
    return None



