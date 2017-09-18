import ConfigParser
import argparse

import logging
import os

import datetime
import time

from beerthday.connectors import ConfluenceConnector
from beerthday.exceptions import ArgRequiredException
from beerthday.holder import Holder
from beerthday.misc import str2bool
from beerthday.notification_executer import NotificationExecuter
from beerthday.senders import EmailSender, SENDERS


def setup_config():
    conf_parser = argparse.ArgumentParser(description='Beerthday buzzer', add_help=False)
    conf_parser.add_argument('--config_file', help='config file', required=True)
    args = conf_parser.parse_args()
    return args.config_file


def setup_params(config_file):
    config = ConfigParser.SafeConfigParser()
    required = ('confluence_url',
                'confluence_user',
                'confluence_pasw',
                'confluence_page_id',
                'confluence_table_indx',
                'confluence_skip_first_row',
                'smtp_host',
                'smtp_port',
                'smtp_user',
                'smtp_pass',
                'smtp_tls',
                'log_file',
                'log_level'
                )

    try:
        config.read([config_file])
        defaults = dict(config.items('Defaults'))
    except ConfigParser.NoSectionError:
        logging.exception('argparse: no section error')
        raise
    for r in required:
        if r not in defaults:
            logging.critical('Arg %s is required but not found' % r)
            raise ArgRequiredException()
    defaults['confluence_skip_first_row'] = str2bool(defaults['confluence_skip_first_row'])
    defaults['smtp_tls'] = str2bool(defaults['smtp_tls'])
    defaults['poll_interval'] = 60
    defaults['push_time']= datetime.time(9, 0)
    return defaults

def setup_logging(params):
    filehandler = logging.FileHandler(filename=params['log_file'])
    logformatter = logging.Formatter('%(asctime)s [%(threadName)-5.12s] [%(levelname)-5.5s]  %(message)s')
    filehandler.setFormatter(logformatter)
    logging.getLogger().addHandler(filehandler)
    logging.getLogger().setLevel(params['log_level'])


def setup_misc(params):
    if not os.path.basename(params['log_file']):
        os.makedirs(os.path.basename(params['log_file']))

class Init(object):
    def __init__(self, params):
        self.params = params
        self.notification_executer = None
        self.holder = None
        self.senders = []
        self.connectors = []

    def __config_senders(self):
        if not self.senders:
            smtp_sender = EmailSender(user=self.params['smtp_user'],
                                      passw=self.params['smtp_pass'],
                                      host=self.params['smtp_host'],
                                      port=self.params['smtp_port'],
                                      tls=self.params['smtp_tls'])
            self.senders.append((SENDERS.EMAIL, smtp_sender))
        return self.senders

    def __config_connectors(self):
        if not self.connectors:
            confluence_connector = ConfluenceConnector(base_url=self.params['confluence_url'],
                                                       user=self.params['confluence_user'],
                                                       passw=self.params['confluence_pasw'],
                                                       page_id=self.params['confluence_page_id'],
                                                       table_indx=self.params['confluence_table_indx'],
                                                       no_first_row=self.params['confluence_skip_first_row'])
            self.connectors.append(confluence_connector)
        return self.connectors

    def config_notification_executer(self):
        if not self.notification_executer:
            self.notification_executer = NotificationExecuter()
        for sender in self.__config_senders():
            self.notification_executer.register_sender(*sender)
        return self.notification_executer

    def config_holder(self):
        if not self.holder:
            self.holder = Holder(self.config_notification_executer())
            for connector in self.__config_connectors():
                self.holder.register_connector(connector)
        return self.holder


def service(time_of_run=None):
    params = setup_params(setup_config())
    setup_misc(params)
    setup_logging(params)
    init = Init(params)
    holder = init.config_holder()
    notification_executer = init.config_notification_executer()
    notification_executer.daemon = True
    notification_executer.start()
    next_poll = 0
    is_pushed = False
    if time_of_run:
        stop_time = time.time() + time_of_run
        service_runned = lambda: time.time() <= stop_time
    else:
        service_runned = lambda:  True

    try:
        while notification_executer.is_alive() and service_runned():
            if next_poll <= time.time():
                next_poll = time.time() + params['poll_interval']
                holder.poll_connectors()
            if params['push_time'].hour == datetime.datetime.now().hour and not is_pushed:
                holder.push_notification()
                is_pushed = True
            elif params['push_time'].hour != datetime.datetime.now().hour:
                is_pushed = False
            time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        logging.critical('User interruption')
    finally:
        notification_executer.service_runned = False
if __name__ == '__main__':
    service()



