import datetime

import time

from beerthday.app import service

import pytest

from test_confluence import prepare_confluence_response

from test_notification_executer import prepare_sender

params = {'push_time': datetime.time(datetime.datetime.now().hour, 0),
          'confluence_url': 'localhost:8090',
          'smtp_port': '465',
          'log_level': 'DEBUG',
          'poll_interval': 60,
          'confluence_skip_first_row': True,
          'smtp_host': 'smtp.gmail.com',
          'confluence_table_indx': '0',
          'confluence_user': '',
          'smtp_pass': '',
          'smtp_tls': False,
          'confluence_page_id': '65586',
          'confluence_pasw': 'test12345',
          'smtp_user': 'antivabo@gmail.com',
          'log_file': '/dev/stdout'}


def run_thread(func):
    from threading import Thread
    from functools import wraps

    @wraps(func)
    def thread_func(*args, **kwargs):
        func_hl = Thread(target=func, args=args, kwargs=kwargs)
        func_hl.daemon = True
        func_hl.start()
        return func_hl

    return thread_func


@pytest.fixture()
def prepare_service(monkeypatch, prepare_sender):
    params['smtp_host'] = prepare_sender[0].addr[0]
    params['smtp_port'] = prepare_sender[0].addr[1]
    monkeypatch.setenv('FAKEDATE', '16-10-2017')
    monkeypatch.setattr('beerthday.app.setup_config', lambda: './beerthday/default.conf')
    monkeypatch.setattr('beerthday.app.setup_params', lambda x: params)
    run_thread(service)(5)
    return prepare_sender[1]


@pytest.mark.gen_test
@pytest.mark.timeout(60)
def test_app(prepare_confluence_response, prepare_service):
    stop_time = time.time() + 10
    while time.time() <= stop_time:
        time.sleep(1)

    assert len(prepare_service) == 5
