import io
import os
import time
from threading import Thread, Lock


##############################################################################
# Log file monitoring
log_lock = Lock()
max_log_lines = 1000
mergedLog = []
filteredLog = []
default_log_filters = [
    "mouth.viseme",
    "mouth.display",
    "mouth.icon",
    "mycroft.identity",
    "mycroft.api:refresh_token",
    "mycroft.client.enclosure",
    "werkzeug",  # personal backend
    "mycroft.skills.skill_manager:_get_skill_directories"
]
log_filters = list(default_log_filters)
log_files = []


def add_log_message(message):
    """ Show a message for the user (mixed in the logs) """
    global filteredLog
    global mergedLog
    global log_lock

    with log_lock:
        message = "@" + message       # the first byte is a code
        filteredLog.append(message)
        mergedLog.append(message)


def clear_log():
    global filteredLog
    global mergedLog
    global log_lock

    with log_lock:
        mergedLog = []
        filteredLog = []


def rebuild_filtered_log():
    global filteredLog
    global mergedLog
    global log_lock

    with log_lock:
        filteredLog = []
        for line in mergedLog:
            # Apply filters
            ignore = False

            # Apply filters
            for filtered_text in log_filters:
                if filtered_text and filtered_text in line:
                    ignore = True
                    break

            if not ignore:
                filteredLog.append(line)


class LogMonitorThread(Thread):
    def __init__(self, filename, logid):
        global log_files
        Thread.__init__(self)
        self.filename = filename
        self.st_results = os.stat(filename)
        self.logid = str(logid)
        log_files.append(filename)

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
            time.sleep(0.1)

    def read_file_from(self, bytefrom):
        global filteredLog
        global mergedLog
        global log_lock

        with io.open(self.filename) as fh:
            fh.seek(bytefrom)
            while True:
                line = fh.readline()
                if line == "":
                    break

                # Allow user to filter log output
                ignore = False
                for filtered_text in log_filters:
                    if filtered_text in line:
                        ignore = True
                        break

                with log_lock:
                    if ignore:
                        mergedLog.append(self.logid + line.rstrip())
                    else:
                        filteredLog.append(self.logid + line.rstrip())
                        mergedLog.append(self.logid + line.rstrip())

        # Limit log to  max_log_lines
        if len(mergedLog) >= max_log_lines:
            with log_lock:
                cToDel = len(mergedLog) - max_log_lines
                if len(filteredLog) == len(mergedLog):
                    del filteredLog[:cToDel]
                del mergedLog[:cToDel]

            # release log_lock before calling to prevent deadlock
            if len(filteredLog) != len(mergedLog):
                rebuild_filtered_log()


def start_log_monitor(filename):
    if os.path.isfile(filename):
        name = os.path.basename(filename).split(".")[0] + " - "
        thread = LogMonitorThread(filename, name)
        thread.setDaemon(True)  # this thread won't prevent prog from exiting
        thread.start()
        return thread
    return None


def get_logs():
    return filteredLog


