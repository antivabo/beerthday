from beerthday import misc
from beerthday.senders import SENDERS

notification_templates = {
    SENDERS.EMAIL: 'Happy birthday to %s!',
    'empty': ''
}


class Notification(object):
    def __init__(self, newborns, recipient):
        self.message = ''
        self.recipient = recipient
        self.type = recipient.contact[0]
        self.args = recipient.contact[1]
        for newborn in newborns:
            self.message = self.message + \
                           '\n' + \
                           notification_templates[self.type] % newborn.name
        # self.notify_on = datetime.datetime.today()
        self.notify_on = misc.today()
        self.id = '%s_%s_%s' % (self.type, self.recipient.id, self.notify_on)
        self.retry_number = 0

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __str__(self):
        return 'Notification id %s: %s, %s, %s' % (
            self.id,
            self.recipient,
            self.type,
            self.notify_on)

    def is_ready(self):
        # return self.notify_on == datetime.date.today()
        print self.notify_on, misc.today(),  self.notify_on == misc.today()
        return self.notify_on == misc.today()

    def is_expired(self):
        print self.notify_on, misc.today(), self.notify_on > misc.today()

        return self.notify_on > misc.today()
