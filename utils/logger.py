from datetime import datetime
from threading import Lock


LOG_FILE = './log.txt'
LOCK = Lock()


def log(message, file=None, printable=True):
    time = datetime.now().strftime('%d.%m.%Y %H:%M')
    log_msg = f'{time} : {message}'

    if printable:
        print(log_msg)

    with LOCK:
        with open(LOG_FILE if file is None else file, 'r+') as f:
            f.seek(0, 2)
            f.write(log_msg)
