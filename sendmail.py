#!/usr/bin/env python3

"""Send the contents of a directory as a MIME message."""

import os
import sys
import smtplib
# For guessing MIME type based on file name extension
import mimetypes

from argparse import ArgumentParser

from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

COMMASPACE = ', '

def send_mail(defargs=None):
    parser = ArgumentParser(description="""\
Send a file as an attachment as a MIME message.
Unless the -o option is given, the email is sent by using the gmail smtp server,
which then does the normal delivery process.  
""")
    parser.add_argument('-f', '--file',
                        help='Attach the specified file.')
    parser.add_argument('-o', '--output',
                        metavar='FILE',
                        help="""Print the composed message to FILE instead of
                        sending the message to the SMTP server.""")
    parser.add_argument('-r', '--recipient', required=True,
                        action='append', metavar='RECIPIENT',
                        default=[], dest='recipients',
                        help='A To: header value (at least one required)')
    parser.add_argument('-s', '--sender', required=True,
                        metavar='SENDER',
                        help='Email address used by gmail smtp to send the mail')
    parser.add_argument('-p', '--password', required=True,
                        metavar='PASSWORD',
                        help='Application (or normal) password for sender gmail account')
    parser.add_argument('-n', '--name')
    args = parser.parse_args(defargs)
    filename = args.file
    # Create the enclosing (outer) message
    outer = MIMEMultipart()
    outer['Subject'] = 'Secret Santa'
    outer['To'] = COMMASPACE.join(args.recipients)
    outer['From'] = 'secretsanta@mail.com'
    outer.attach(MIMEText('Hi {}!\n\nThis is your Secret Santa information.\n\nGood luck, and merry holidays!'.format(args.name)))
    outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    path = filename
    if not os.path.isfile(path):
        print('[ERROR]: {}: no such file'.format(filename))
        exit(1)
    # Guess the content type based on the file's extension.  Encoding
    # will be ignored, although we should check for simple things like
    # gzip'd or compressed files.
    ctype, encoding = mimetypes.guess_type(path)
    if ctype is None or encoding is not None:
        # No guess could be made, or the file is encoded (compressed), so
        # use a generic bag-of-bits type.
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':
        with open(path) as fp:
            # Note: we should handle calculating the charset
            msg = MIMEText(fp.read(), _subtype=subtype)
    elif maintype == 'image':
        with open(path, 'rb') as fp:
            msg = MIMEImage(fp.read(), _subtype=subtype)
    elif maintype == 'audio':
        with open(path, 'rb') as fp:
            msg = MIMEAudio(fp.read(), _subtype=subtype)
    else:
        with open(path, 'rb') as fp:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(fp.read())
        # Encode the payload using Base64
        encoders.encode_base64(msg)
    # Set the filename parameter
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    outer.attach(msg)
    # Now send or store the message
    composed = outer.as_string()
    if args.output:
        with open(args.output, 'w') as fp:
            fp.write(composed)
    else:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.ehlo()
            s.login(args.sender, args.password)
            s.sendmail(args.sender, args.recipients, composed)
