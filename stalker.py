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

# SETTINGS
# Customize these strings for your setup.
stalked_file   = ""
saved_name     = ""
wait_time      = 60

email_address     = ""
email_imap_server = ""
email_smtp_server = ""
email_password    = ""
email_subject     = ""

sysadmin_name  = ""
sysadmin_email = ""


import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders as Encoders
def send_mail(send_from, send_to, subject, text, files=[], server=email_smtp_server):
    assert type(send_to)==list
    assert type(files)==list

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = ', '.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    smtp = smtp = smtplib.SMTP_SSL(server, 465)
    smtp.login(send_from, email_password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

import imaplib
import email
def get_mail_subjects(server, user, password):
    def extract_body(payload):
        if isinstance(payload,str):
            return payload
        else:
            return '\n'.join([extract_body(part.get_payload()) for part in payload])

    emails = []

    conn = imaplib.IMAP4_SSL(server, 993)
    conn.login(user, password)
    conn.select()
    typ, data = conn.search(None, 'UNSEEN')
    try:
        for num in data[0].split():
            typ, msg_data = conn.fetch(num, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(response_part[1].decode())
                    s = msg['from']
                    emails.append((msg['subject'], s[s.rfind("<")+1:s.rfind(">")]))
            typ, response = conn.store(num, '+FLAGS', r'(\Seen)')
    finally:
        try:
            conn.close()
        except:
            pass
        conn.logout()
    return emails


import hashlib
from functools import partial
def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()


import urllib.request
import time
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
                newhash = md5sum(saved_name)
                if newhash != currenthash:
                    currenthash = newhash
                    # Keep a copy
                    new_name = time.strftime("%Y%m%d-%H%M_", time.gmtime()) + saved_name
                    currentfilename = new_name
                    os.rename(saved_name, new_name)
                    # And send everyone a copy
                    print("Sending emails!")
                    send_mail(email_address, subscribers, email_subject, "", files=[new_name])
                else:
                    os.unlink(saved_name)
            except URLError:
                pass
            for i in range(10):
            # Check for new subscribers
                tasks = get_mail_subjects(email_imap_server, email_address, email_password)
                for (task, address) in tasks:
                    task = task.lower()
                    if task == "unsubscribe":
                        print("Unsubscribing", address)
                        subscribers = list(filter(lambda a: a != address, subscribers))
                        send_mail(email_address, [address], email_subject + " - Unsubscribed!",
                                  "You are now unsubscribed!")
                    elif task == "subscribe":
                        print("Subscribing", address)
                        subscribers.append(address)
                        send_mail(email_address, [address], email_subject + " - Subscribed!",
                                  "You are now subscribed!  Send a similar message saying UNSUBSCRIBE to cancel.\nSysadmin:\n"+sysadmin_name+'\n'+sysadmin_email,
                                  files=[currentfilename])
                    else:
                        send_mail(email_address, [address], email_subject + " - Huh?", "Valid subjects are SUBSCRIBE and UNSUBSCRIBE.  Messages must have an empty body.")
                    # And sleep
                    time.sleep(wait_time)
    except KeyboardInterrupt:
        with open('hash.txt', 'w') as f:
            f.write(currenthash + '\n')
            f.write(currentfilename + '\n')
        with open('users.txt', 'w') as f:
            for address in subscribers:
                f.write(address + '\n')
        print("Got Ctrl+C, saved info!")

if __name__ == "__main__":
    main()
