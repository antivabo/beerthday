import logging

import threading

import time

from beerthday.exceptions import NotReadyNotificationException, StaleNotificationException


class NotificationExecuter(threading.Thread):
    def __init__(self):
        super(NotificationExecuter, self).__init__()
        self.senders = {}
        self.process_queue = set([])
        self.max_tries = 10
        self.service_runned = True
        self.cleanup_list = set([])

    def register_sender(self, notification_type, sender):
        self.senders[notification_type] = sender

    def add(self, notification):
        self.process_queue.add(notification)

    def process(self):
        for notification in self.process_queue:
            try:
                if notification.retry_number <= self.max_tries:
                    self.senders[notification.type].send(notification)
                    self.cleanup_list.add(notification)
                    logging.debug('Notification %s successfully sent via %s' % (
                        notification,
                        self.senders[notification.type].__class__.__name__))
                else:
                    logging.warning('Max retries exceeded, remove notification %s' % notification)
                    self.cleanup_list.add(notification)
            except StaleNotificationException:
                print 'aaa', notification
                self.cleanup_list.add(notification)
            except NotReadyNotificationException:
                pass
            except KeyError:
                notification.retry_number += 1
                logging.warning('No suitable sender for notification type %s' % notification.type)
            except Exception as e:
                notification.retry_number += 1
                logging.warning('Error in sender %s: %s ' % (notification.type, e))

    def cleanup(self):
        for notification in self.cleanup_list:
            self.process_queue.remove(notification)
        self.cleanup_list = set([])

    def run(self):
        logging.info('%s started' % __name__)
        while self.service_runned:
            self.process()
            self.cleanup()
            time.sleep(1)
