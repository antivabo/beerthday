import datetime

import os


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def str2bool(_str):
    return _str.lower() in ('yes', 'true', 't', '1', 'y')


def today():
    if 'FAKEDATE' in os.environ:
        return datetime.datetime.strptime(os.getenv('FAKEDATE'), '%d-%m-%Y').date()
    else:
        return datetime.date.today()
