#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


import re
import datetime


def parse_timedelta(deltatime_str):
    """
    Converts a string object of format (DD days, hh:mm:ss) to timedelta object.

    If the number of hours / minutes / seconds is specified more than 24/60/60 respectively,
    parser will automatically drop the extra ones to the next rank.

    An OverflowError will be raised if the number of days is not in the range
    -999999999 <= days <= 999999999.
    """
    list_days_hours_minutes_seconds = re.findall(r"\d+", deltatime_str)

    days = int(list_days_hours_minutes_seconds[0])
    hours = int(list_days_hours_minutes_seconds[1])
    minutes = int(list_days_hours_minutes_seconds[2])
    seconds = int(list_days_hours_minutes_seconds[3])

    return datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
