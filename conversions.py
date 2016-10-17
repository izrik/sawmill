#!/usr/bin/env python

from dateutil.parser import parse as dparse
from datetime import datetime


def str_from_datetime(dt):
    if dt is None:
        return None
    return str(dt)


def datetime_from_str(s):
    if s is None:
        return None
    if not isinstance(s, datetime):
        return dparse(s).replace(tzinfo=None)
    return s


def bool_from_str(s):
    if isinstance(s, basestring):
        s = s.lower()
    if s in ['true', 't', '1', 'y']:
        return True
    if s in ['false', 'f', '0', 'n']:
        return False
    return bool(s)
