class BeerthdayException(Exception):
    """Root Beerthday Exception"""


class StaleNotificationException(BeerthdayException):
    """StaleNotificationException"""


class NotReadyNotificationException(BeerthdayException):
    """NotReadyNotificationException"""


class WrongArgsException(BeerthdayException):
    """WrongArgsException"""


class ArgRequiredException(BeerthdayException):
    """ArgRequiredException"""
