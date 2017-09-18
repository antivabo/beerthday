import datetime

import locale

from beerthday.entry import Entry
from beerthday.notification import Notification
from beerthday.notification_executer import NotificationExecuter
from beerthday.senders import SENDERS
from beerthday.senders.smtp import EmailSender

import pytest


locale.setlocale(locale.LC_ALL, 'ru_RU.UTF8')

entry_list = [Entry(1,
                    'TestName',
                    (SENDERS.EMAIL, 'test@test.com'),
                    datetime.datetime.now()),
              Entry(2,
                    'OtherName',
                    (SENDERS.EMAIL, 'other@test.com'),
                    datetime.datetime.strptime('01.02.1990', '%x')),
              Entry(3,
                    'OtherName2',
                    (SENDERS.EMAIL, 'other@test.com'),
                    datetime.datetime.strptime('01.02.1990', '%x'))]


@pytest.fixture()
def prepare_sender(smtpserver):
    return smtpserver, smtpserver.outbox


@pytest.mark.gen_test
def test_holder(prepare_sender):
    notification = Notification(set(entry_list), entry_list[2])
    notification_executer = NotificationExecuter()
    notification_executer.register_sender(SENDERS.EMAIL, EmailSender(user='',
                                                                     passw='',
                                                                     host=prepare_sender[0].addr[0],
                                                                     port=prepare_sender[0].addr[1],
                                                                     tls=False))
    notification_executer.add(notification)
    notification_executer.process()
    assert prepare_sender[1][0]['To'] == entry_list[2].contact[1]
