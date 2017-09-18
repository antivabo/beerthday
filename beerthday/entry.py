import datetime

from beerthday import misc


class Entry(object):
    def __init__(self, _id, name, contact, birthday):
        self.id = int(_id)
        self.name = name
        self.contact = contact
        self.birthday = birthday

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
        return 'Entry id %s: %s, %s, %s' % (self.id, self.name, self.contact, self.birthday)

    def __repr__(self):
        return str((self.id, self.name, self.contact, self.birthday))

    def is_birthday(self):
        if not self.birthday:
            return False
        # today = datetime.datetime.today()
        today = misc.today()
        start = datetime.timedelta(days=7)
        end = datetime.timedelta(days=1)

        try:
            self.birthday = self.birthday.replace(year=datetime.date.today().year)
        except ValueError:
            self.birthday = self.birthday.replace(month=2,
                                                  day=28,
                                                  year=datetime.date.today().year)
        return today - start <= self.birthday <= today + end
