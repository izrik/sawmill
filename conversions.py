#!/usr/bin/env python


def str_from_datetime(dt):
    if dt is None:
        return None
    return str(dt)


def bool_from_str(s):
    if isinstance(s, basestring):
        s = s.lower()
    if s in ['true', 't', '1', 'y']:
        return True
    if s in ['false', 'f', '0', 'n']:
        return False
    return bool(s)
