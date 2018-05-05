# Title: cleanup.py
#
# Author: Troy <twc17@pitt.edu>
# Date Modified: 05/05/2018
# Version: 1.0.0
#
# Purpose:
#   This helper script will check the current running Redis DB for users
#   that have been logged in for an extended period of time, then auto log them out

# Imports
from main import *

# Number of minutes before user will be logged out
# Default is 12 hours (720 min)
TIMEOUT = 720

# Timestamp format that is being used by program
FORMAT = '%Y-%m-%d %H:%M:%S'

def compare_time(t1, t2):
    """Compare two timestamps, return difference in minutes

    Arguments:
        t1 -- First time stamp, as string
        t2 -- Second time stamp, as string

    Returns:
        minutes -- Difference between two times, in minutes
    """
    compare1 = datetime.datetime.strptime(t1, FORMAT)
    compare2 = datetime.datetime.strptime(t2, FORMAT)

    if compare1 > compare2:
        diff = compare1 - compare2
    else:
        diff = compare2 - compare1

    return int(round(diff.total_seconds() / 60))


def main():
    now = datetime.datetime.now().strftime(FORMAT)

    for key in db.keys():
        key = key.decode('utf-8')
        data = db.lrange(key, 0, -1)
        user_line = [key, data[0].decode('utf-8'), data[1].decode('utf-8'), data[2].decode('utf-8')]

        if compare_time(now, user_line[3]) > TIMEOUT:
            del_log(key, db)
            user_line.append("OUT (AUTO)")
            write_log(user_line, log_file)

if __name__ == "__main__":
    main()
