import datetime

import locale

from beerthday.entry import Entry
from beerthday.senders import SENDERS

from dateutil.relativedelta import relativedelta

from freezegun import freeze_time

import pytest


@pytest.mark.gen_test
def test_entry():
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF8')
    assert Entry(1, 'TestName', (SENDERS.EMAIL, 'test@test.com'), datetime.datetime.strptime('01.02.1990', '%x')) == \
           Entry(1, 'OtherName', (SENDERS.EMAIL, 'test@test.com'), datetime.datetime.strptime('01.02.1990', '%x'))


@freeze_time('Feb 29th, 2016')
@pytest.mark.parametrize('years,days', [
    (-4, -7),
    (-4, 1),
    (-5, -6),
    (-5, 1)])
@pytest.mark.gen_test
def test_entry_leap(years, days):
    assert Entry(1,
                 'TestName',
                 ('email', 'test@test.com'),
                 datetime.datetime.now().date() + relativedelta(years=years, days=days)).is_birthday()


@freeze_time('Feb 28th, 2016')
@pytest.mark.parametrize('years,days', [
    (-4, -7),
    (-4, 1),
    (-5, -7),
    (-5, 0)])
@pytest.mark.gen_test
def test_entry_nonleap(years, days):
    assert Entry(1,
                 'TestName',
                 ('email', 'test@test.com'),
                 datetime.datetime.now().date() + relativedelta(years=years, days=days)).is_birthday()
    assert not Entry(1,
                     'TestName',
                     ('email', 'test@test.com'),
                     None).is_birthday()
