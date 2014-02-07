URL Stalker is a simple program that, simply put, stalks a URL and knows immediately
when it changes.  Every ten minutes (configurable), the program downloads the file and
compares it to the old one.  If it has changed, it emails all subscribers with a copy 
of the new file.  It needs its own email address, and all interaction with it is 
performed by sending it pithy messages over email.

Pull requests and bug reports are welcome.  I'll update this as I need it, but it's 
otherwise not being actively developed.

To set it up, check the source code out into a directory somewhere, then edit 
`settings.py` to your satisfaction.  You will need to provide it an email address with
SMTP and IMAP access.  Gmail works well (in fact, this isn't tested with anything 
else!)

The general settings are:
 - `stalked_file`:  The URL of the file to stalk
 - `saved_name`:    URL Stalker keeps a timestamped copy of each version, with this
                    base name.
 - `wait_time`:     Time between email queries

Email specific settings are:
 - `email_address`:     The URL Stalker's email address, used for "From" field
 - `email_imap_server`: The IMAP server to connect to
 - `email_smtp_server`: The SMTP server to connect to
 - `email_password`:    Password to the SMTP and IMAP accounts
 - `email_subject`:     Base subject to use ("URL Stalker" works)

You should also fill out the `sysadmin_name` and `sysadmin_email` fields so people 
can contact you if the need arises.
