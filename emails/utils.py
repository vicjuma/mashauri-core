from datetime import timedelta

from django.utils.timezone import now

import smtplib
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from django.core.files.base import ContentFile
from email import encoders
import os
import ssl


def send_mail(recipients, subject, message):
    # try:
    if settings.MAIL_SSL:
        server_type = smtplib.SMTP_SSL
    else:
        server_type = smtplib.SMTP

    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = ', '.join(
        recipients) if isinstance(
            recipients, list) else recipients
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))
    print("=============== DEBUG 1 =====================")
    
    # try:
    with server_type(
        settings.MAIL_HOST_SERVER,
        settings.EMAIL_HOST_PORT,
        context=ssl.create_default_context(),
    ) as server:
        print("=============== DEBUG 2 =====================")
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

        print(recipients, "=================")

        refused = server.sendmail(settings.EMAIL_HOST_USER, recipients, msg.as_string())

        print("SMTP refused recipients:", refused)
        print("Email submitted to SMTP for:", recipients)

    print(f"Email sending attempt completed for {recipients}")