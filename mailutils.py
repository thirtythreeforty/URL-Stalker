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

import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders as Encoders
def send_mail(send_from, send_to, subject, text, server, email_password, files=[], hide=False):
    assert type(send_to)==list
    assert type(files)==list
    assert type(hide)==bool

    msg = MIMEMultipart()
    msg['From'] = send_from
    if not hide:
        # Basically BCC the messages by leaving this out.
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
