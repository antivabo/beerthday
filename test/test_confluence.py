import pickle

import datetime

from beerthday.connectors import ConfluenceConnector

import pytest

from beerthday.entry import Entry


@pytest.fixture(scope='function')
def prepare_confluence_response(monkeypatch):
    with open('./test/res/confluence.json') as f:
        confluence_response = pickle.load(f)

        class DummyResponse:

            def json(self):
                return confluence_response
        monkeypatch.setattr('requests.get',
                            lambda *args, **kwargs: DummyResponse())


@pytest.mark.gen_test
def test_confluence(prepare_confluence_response):
    confluence_connector = ConfluenceConnector('base_url',
                                               'user',
                                               'passw',
                                               'page_id')
    assert confluence_connector.poll() == [Entry(1, 'Ivanov Leonid', ('email', 't@mt.ru'), datetime.date(1900, 10, 16)),
                                           Entry(2, 'Ivanov Vitalii', ('email', 'v@mt.ru'), datetime.date(1900, 8, 2)),
                                           Entry(3, "Ivanov Il'dar", ('email', 'i@mt.ru'), datetime.date(1900, 6, 26)),
                                           Entry(4, 'Ivanov Andrei', ('email', 'a@mt.ru'), datetime.date(1900, 5, 29)),
                                           Entry(5, 'Ivanov Aleksei', ('email', 'aa@mt.ru'), datetime.date(1900, 5, 25)),
                                           Entry(7, 'Ivanov Anton', ('email', 'ag@mt.ru'), None)]
