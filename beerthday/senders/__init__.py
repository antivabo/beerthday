from enum import Enum

from beerthday.senders.smtp import EmailSender


class SENDERS(Enum):
    EMAIL = ('email')

