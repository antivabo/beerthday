import datetime

import locale

from beerthday.connectors.confluence import Connector
from beerthday.entry import Entry
from beerthday.holder import Holder
from beerthday.notification_executer import NotificationExecuter
from beerthday.senders import SENDERS

import pytest


locale.setlocale(locale.LC_ALL, 'ru_RU.UTF8')
entry_list = [Entry(1,
                    'TestName',
                    (SENDERS.EMAIL, 'test@test.com'),
                    datetime.datetime.now().date()),
              Entry(2,
                    'OtherName',
                    (SENDERS.EMAIL, 'other@test.com'),
                    datetime.datetime.strptime('01.02.1990', '%x').date())]

entry_list2 = [Entry(1,
                     'TestName',
                     (SENDERS.EMAIL, 'test@test.com'),
                     datetime.datetime.now().date()),
               Entry(2,
                     'OtherName',
                     (SENDERS.EMAIL, 'other@test.com'),
                     datetime.datetime.strptime('01.02.1990', '%x').date()),
               Entry(3,
                     'OtherName2',
                     (SENDERS.EMAIL, 'other@test.com'),
                     datetime.datetime.strptime('01.02.1990', '%x').date())]


@pytest.fixture()
def prepare_holder():
    notification_executer = NotificationExecuter()
    Holder.__metaclass__._instances = {}
    holder = Holder(notification_executer)
    yield holder, notification_executer
    holder.__class__.__metaclass__._instances = {}


@pytest.fixture(scope='function')
def fake_connector(request):

    class FakeConnector(Connector):
        def __init__(self, val):
            self.val = val

        def poll(self):
            return self.val
    return (FakeConnector(entry_list), FakeConnector(entry_list2))


@pytest.mark.gen_test
def test_holder(fake_connector, prepare_holder):
    holder = prepare_holder[0]
    notification_executer = prepare_holder[1]
    for connector in fake_connector:
        holder.register_connector(connector)
    holder.poll_connectors()
    holder.push_notification()
    assert len(notification_executer.process_queue) == 2
    for notification in notification_executer.process_queue:
        assert notification.is_ready()
        assert notification.recipient in entry_list2[1:]
        notification.notify_on = datetime.date.today() - datetime.timedelta(days=1)
        assert not notification.is_expired()
        notification.notify_on = datetime.date.today() + datetime.timedelta(days=1)
        assert not notification.is_ready()
