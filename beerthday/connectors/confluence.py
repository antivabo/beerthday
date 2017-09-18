import base64

import datetime

import logging

import re


from beerthday.entry import Entry
from beerthday.senders import SENDERS

from bs4 import BeautifulSoup

import requests

import unidecode as unidecode


class Connector(object):

    def get_entries(self):
        raise NotImplemented


class ConfluenceConnector(Connector):
    SENDER = SENDERS.EMAIL

    def __init__(self,
                 base_url,
                 user,
                 passw,
                 page_id,
                 table_indx=0,
                 no_first_row=True):
        self.base_url = base_url
        self.user = user
        self.passw = passw
        self.page_id = page_id
        self.no_first_row = no_first_row
        self.table_indx = int(table_indx)

    @staticmethod
    def __transform(raw_entry):
        def select_sender(contact):
            return (ConfluenceConnector.SENDER, contact)

        def birthday(birthday_str):
            if not birthday_str.strip():
                return None
            try:
                return datetime.datetime.strptime(birthday_str, '%x').date()
            except ValueError:
                return datetime.datetime.strptime(birthday_str, '%d.%m').date()

        result = {}
        transformation = {
            0: ('_id', str),
            1: ('name', str),
            4: ('contact', select_sender),
            7: ('birthday', birthday)}
        for i in range(len(raw_entry)):
            try:
                if transformation[i][1]:
                    result[transformation[i][0]] = (transformation[i][1](unidecode.unidecode(raw_entry[i])))
                else:
                    result[transformation[i][0]] = raw_entry[i]
            except KeyError:
                pass
        return result

    @staticmethod
    def __table_to_list(table, start_result_from):
        result = []
        for row in table.find_all('tr')[start_result_from:]:
            _row = []
            if re.match('.*line-through.*', str(row)):
                continue
            for col in row.find_all('td'):
                _row.append(col.get_text())
            raw_entry = ConfluenceConnector.__transform(_row)

            if raw_entry:
                result.append(Entry(**raw_entry))
        return result

    def __get_html(self):
        base64string = base64.encodestring('%s:%s' % (self.user, self.passw)).replace('\n', '')
        headers = {'content-type': 'application/json',
                   'Authorization': 'Basic %s' % base64string}

        return requests.get('http://%s/rest/api/content/%s?expand=body.storage' % (self.base_url, self.page_id),
                            headers=headers).json()['body']['storage']['value']

    def poll(self):
        soup = BeautifulSoup(self.__get_html(), 'html.parser')
        table = soup.find_all('table')[self.table_indx].find_all('tbody')[0]
        result = [i for i in self.__table_to_list(table, int(self.no_first_row))]
        logging.debug('Poll results in %s: %s' % (self.__class__.__name__, result))
        return result
