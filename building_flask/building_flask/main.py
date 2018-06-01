# Title: main.py
#
# Author: Troy <twc17@pitt.edu>
# Date Modified: 04/25/2018
# Version: 2.0.0
#
# Purpose:
#   This is a program for a building access log book. It uses a magnetic card reader to grab
#   a Pitt employees 2P number from their ID card. This will then be used for a HTTPS GET request to
#   get the rest of their account information. You also have the option to manually enter in
#   information for guests, or if you forgot your ID card.

# Import libs
from flask import Flask, request, render_template, redirect, url_for
import xml.etree.ElementTree as etree
import os
import socket
import sys
import datetime
import time
import requests
import redis

app = Flask(__name__)

# Load the configurations
app.config.from_pyfile('config_file.cfg')
title = app.config['TITLE']
server = app.config['API_SERVER']
call = app.config['API_CALL']
log_file = app.config['LOG_DIR'] + 'building_access.log'
swipe_log_file = app.config['LOG_DIR'] + 'swipe.log'

# Redis configurations
redis_server = os.environ['REDIS']

# Redis connection
try:
    if "REDIS_PWD" in os.environ:
        db = redis.StrictRedis(host=redis_server, port=6379, password=os.environ['REDIS_PWD'])
    else:
        db = redis.Redis(redis_server)
    db.ping()
except redis.ConnectionError:
    exit('Failed to connect to Redis, terminating!')

def query_ws(card_number):
    """Query Pitt web services (maybe?) server for users 2P number

    Arguments:
        card_number -- Pitt 2P number from ID card

    Returns:
        Result of query, as string
    """
    payload = {'search': card_number, 'signon': ''}
    result = requests.get('https://' + server + '/' + call, params=payload)
    result = result.content
    tree = etree.fromstring(result)
    pitt_user = [None] * 3

    if len(tree) == 0:
        return pitt_user

    for ele in tree[0]:
        if ele.tag.find("username") is not -1:
            pitt_user[0] = ele.text
        if ele.tag.find("firstName") is not -1:
            pitt_user[1] = ele.text
        if ele.tag.find("lastName") is not -1:
            pitt_user[2] = ele.text

    return pitt_user

def add_log(user, first, last, company, db):
    """Add record to current building access log

    Arguments:
        user -- Pitt Username
        first -- First name
        last -- Last name
        company -- Company name
        db -- Database of current building log

    Returns:
        True if the add is successful, False otherwise
    """
    # Format the time 2013-09-18 11:16:32
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return db.lpush(user, *[now, last, first])

def del_log(user, db):
    """Delete record from the current building access log

    Arguments:
        user -- Pitt username to logout
        db -- Database of current building log

    Return:
        True if the delete is successful, False otherwise
    """
    return db.delete(user)

def write_log(entry, log_file):
    """Write add/del entry to log file

    Arguments:
        entry -- Entry to add to log file
                Will probably look something like 'USER,last,first,IN/OUT,date'
        log_file -- Log file to write entry to

    Return:
        True if write to log file was successful, False otherwise
    """
    # Open out log_file to work with
    log_file = open(log_file, 'a')
    # Format the time 2013-09-18 11:16:32
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = ",".join(entry)
    log_file.write(now + "," + entry + "\n")
    log_file.close()

def sort_log(db):
    building_log = []
    users = []

    for key in db.keys():
        key = key.decode('utf-8')
        data = db.lrange(key, 0, -1)
        bytedata = b','.join(data)
        user_line = key + "," + bytedata.decode('utf-8')
        building_log.append(user_line)

    # Sort list based on date/time stamp
    building_log.sort(key = lambda x: str(x.split(',')[4][-20:]), reverse=True)

    for person in building_log:
        users.append(person.split(','))

    return users

def process_input(user_input):
    if len(user_input) == 0:
        entry = ["GUEST"]
        write_log(entry, swipe_log_file)
        return "GUEST"
    else:
        card_number = user_input.split('=')
        if len(card_number) == 2 and card_number[0][1:].isdigit():
            entry = [user_input]
            write_log(entry, swipe_log_file)
            return card_number[0][-10:]
        else:
            entry = ["ERROR"]
            write_log(entry, swipe_log_file)
            return "ERROR"

@app.route('/guest', methods=['GET', 'POST'])
def guest():

    # Handle GET reqeust
    if request.method == 'GET':
        # Return the HTML page for guest logins
        return render_template("guest.html", title=title)

    # POST request of user singing in
    if request.method == 'POST':

        if request.form['button'] == 'home':
            return redirect(url_for('index'))

        # Add guest to DB, return index page
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        company = request.form['company']

        if first_name == '' or last_name == '':
            return render_template("guest.html", title=title)

        username = first_name[0].upper() + last_name.upper()

        guest = [username, first_name, last_name, company]

        if db.exists(guest[0]) == 1:
            del_log(guest[0], db)
            guest.append("OUT")
            write_log(guest, log_file)
        else:
            add_log(guest[0], guest[1], guest[2], db)
            guest.append("IN")
            write_log(guest, log_file)

        return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():

    # Handle GET requests
    if request.method == 'GET':
        # Print out the current building log
        # Have a 'hidden' input field for card swipe (this will be in the HTML file)
        # return index page
        building_log = sort_log(db)
        return render_template("index.html", title=title, building_log=building_log)

    # Handle POST requests
    elif request.method == 'POST':
        # Validate and process the users input
        # Either log user in, out, or add guest
        # if guest: return guest_login page
        # if pitt_employee: add or remove from log and return index
        user_input = process_input(request.form['user_input'])

        if user_input == 'GUEST':
            return redirect(url_for('guest'))
        elif user_input == 'ERROR':
            building_log = sort_log(db)
            return render_template("index.html", title=title, building_log=building_log, error="Error reading card")
        else:
            pitt_user = query_ws("2P00" + user_input + "*")
            
            if pitt_user[0] is None:
                building_log = sort_log(db)
                return render_template("index.html", title=title, building_log=building_log, error="Error with web query!")

            # Check to to see if the user scanned from ID card is logged in
            # If they are, remove them from the current building log
            if db.exists(pitt_user[0]) == 1:
                del_log(pitt_user[0], db)
                pitt_user.append("OUT")
                write_log(pitt_user, log_file)
                msg = pitt_user[0] + " logged OUT"
                building_log = sort_log(db)
                return render_template("index.html", title=title, building_log=building_log, info=msg)

            # Else add the user to the current building log
            else:
                add_log(pitt_user[0], pitt_user[1], pitt_user[2], db)
                pitt_user.append("IN")
                write_log(pitt_user, log_file)
                msg = pitt_user[0] + " logged IN"
                building_log = sort_log(db)
                return render_template("index.html", title=title, building_log=building_log, message=msg)

if __name__ == "__main__":
    app.run()
