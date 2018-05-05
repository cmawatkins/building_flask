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
import datetime
import redis

