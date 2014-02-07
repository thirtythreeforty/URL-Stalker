#!/usr/bin/python3

#   This file is part of the URL Stalker.

#   URL Stalker is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   URL Stalker is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.

#   You should have received a copy of the GNU Affero General Public License
#   along with URL Stalker.  If not, see <http://www.gnu.org/licenses/>.

import urllib.request
import time
import os
import mailutils
import hashutils
from settings import *

def saveData(currenthash, currentfilename, subscribers):
    '''Helper function for main()'''
    with open('hash.txt', 'w') as f:
        f.write(currenthash + '\n')
        f.write(currentfilename + '\n')
    with open('users.txt', 'w') as f:
        for address in subscribers:
            f.write(address + '\n')

def main():
    currenthash = ""
    currentfilename = ""
    subscribers = []

    # Retrieve list of users from file, and current hash from another file
    try:
        with open('users.txt', 'r') as f:
            subscribers = f.readlines()
            subscribers = [l.strip() for l in subscribers]
    except FileNotFoundError:
        pass
    try:
        with open('hash.txt', 'r') as f:
            currenthash = f.readline().strip()
            currentfilename = f.readline().strip()
    except FileNotFoundError:
        pass

    try:
        while True:
            # Download the file
            try:
                urllib.request.urlretrieve(stalked_file, saved_name)
                newhash = hashutils.md5sum(saved_name)
                if newhash != currenthash:
                    currenthash = newhash
                    # Keep a copy
                    new_name = time.strftime("%Y%m%d-%H%M_", time.gmtime()) + saved_name
                    currentfilename = new_name
                    os.rename(saved_name, new_name)
                    saveData(currenthash, currentfilename, subscribers)
                    # And send everyone a copy
                    print("Sending emails!")
                    mailutils.send_mail(email_address,
                                        subscribers,
                                        email_subject + " - Update!",
                                        "",
                                        email_smtp_server,
                                        files=[new_name],
                                        hide=True)
                else:
                    os.unlink(saved_name)
            except:
                pass
            for i in range(10):
                try:
                    # Check for new subscribers
                    tasks = mailutils.get_mail_subjects(email_imap_server, email_address, email_password)
                    for (task, address) in tasks:
                        if address == email_address:
                            # Skip emails from self
                            continue
                        task = task.lower().strip()
                        if task == "unsubscribe":
                            print("Unsubscribing", address)
                            subscribers = list(filter(lambda a: a != address, subscribers))
                            mailutils.send_mail(email_address,
                                                [address],
                                                email_subject + " - Unsubscribed!",
                                                "You are now unsubscribed!",
                                                email_smtp_server)
                        elif task == "subscribe":
                            print("Subscribing", address)
                            subscribers.append(address)
                            mailutils.send_mail(email_address,
                                                [address],
                                                email_subject + " - Subscribed!",
                                                "You are now subscribed!  Send a similar message saying UNSUBSCRIBE to cancel." +
                                                "\n\nSysadmin:\n"+sysadmin_name+'\n'+sysadmin_email +
                                                "\n\nURL Stalker is open source under the AGPLv3!\nSee github.com/thirtythreeforty/URL-Stalker for the code.",
                                                email_smtp_server,
                                                files=[currentfilename])
                        else:
                            mailutils.send_mail(email_address,
                                                [address],
                                                email_subject + " - Huh?",
                                                "Valid subjects are SUBSCRIBE and UNSUBSCRIBE.  Messages must have an empty body.",
                                                email_smtp_server)
                    if len(tasks) > 0:
                        saveData(currenthash, currentfilename, subscribers)
                except:
                    pass
                # And sleep
                time.sleep(wait_time)
    except KeyboardInterrupt:
        saveData(currenthash, currentfilename, subscribers)
        print(" Got Ctrl+C, saved info!")

if __name__ == "__main__":
    main()
