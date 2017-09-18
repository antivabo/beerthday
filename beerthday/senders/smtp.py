import logging

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from beerthday.exceptions import NotReadyNotificationException, StaleNotificationException


class Sender(object):
    def __init__(self, *args, **kwargs):
        raise NotImplemented

    def send(self, notification):
        logging.debug('Try to send notification %s via %s' % (notification, self.__class__.__name__))
        if notification.is_expired():
            logging.info('Notification %s is expired' % notification)
            raise StaleNotificationException()
        if not notification.is_ready():
            logging.info('Notification %s is not ready yet' % notification)
            raise NotReadyNotificationException()


class EmailSender(Sender):
    def __init__(self, user, passw, host, port, tls=True):

        self.user = user
        self.passw = passw
        self.host = host
        self.port = port
        self.tls = tls

    def send(self, notification):
        super(EmailSender, self).send(notification)

        message = MIMEMultipart()
        message['From'] = self.user
        message['To'] = notification.args
        message['Subject'] = 'Birthday list'
        body = notification.message
        message.attach(MIMEText(body, 'plain'))
        message = message.as_string()

        server = smtplib.SMTP(self.host, self.port)
        if self.tls:
            server.starttls()
        if self.user and self.passw:
            server.login(self.user, self.passw)
        server.sendmail(self.user, notification.args, message)
        server.quit()

        logging.debug('Message %s,  sent via %s' % (
            message,
            self.__class__.__name__
        ))
