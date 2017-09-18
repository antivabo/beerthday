
from beerthday import misc
from beerthday.misc import Singleton

from notification import Notification


class Holder(object):
    __metaclass__ = Singleton

    def __init__(self, notification_executer):
        self.__list = {}
        self.notification_executer = notification_executer
        self.connectors = set([])

    def __add(self, entry):
        self.__list.add(entry)

    def __remove(self, entry):
        if entry in self.__list:
            self.__list.remove(entry)

    def __add_batch(self, *args):
        self.__list = self.__list.union(set(args))

    def __flush(self):
        self.__list = set([])

    def __get_newborns_list(self):
        return set([entry for entry in self.__list if entry.is_birthday()])

    def __str__(self):
        return str(self.__list)

    def register_connector(self, connector):
        self.connectors.add(connector)

    def unregister_connector(self, connector):
        if connector in self.connectors:
            self.connectors.remove(connector)

    def complete_clear(self):
        self.__flush()
        self.connectors = set([])

    def poll_connectors(self):
        self.__flush()
        for connector in self.connectors:
            self.__add_batch(*connector.poll())

    def push_notification(self):
        # if datetime.date.today().weekday() > 5:
        if misc.today().weekday() > 5:
            return
        newborns_list = self.__get_newborns_list()
        for recipient in self.__list:
            if newborns_list - {recipient}:
                self.notification_executer.add(Notification(newborns_list - {recipient},
                                                            recipient))
