"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/6/22 下午5:04
"""


def seconds_to_dhms_zh(seconds):
    def _days(day):
        return "{}天, ".format(day)

    def _hours(hour):
        return "{}小时, ".format(hour)

    def _minutes(minute):
        return "{}分钟, ".format(minute)

    def _seconds(second):
        return "{}秒".format(second)

    days = seconds // (3600 * 24)
    hours = (seconds // 3600) % 24
    minutes = (seconds // 60) % 60
    seconds %= 60
    if days > 0:
        return _days(days) + _hours(hours).strip(', ')
    if hours > 0:
        return _hours(hours) + _minutes(minutes).strip(', ')
    if minutes > 0:
        return _minutes(minutes) + _seconds(seconds)

    return _seconds(seconds)


def seconds_to_dhms_en(seconds):
    def _days(day):
        return "{} days, ".format(day) if day > 1 else "{} day, ".format(day)

    def _hours(hour):
        return "{} hours, ".format(hour) if hour > 1 else "{} hour, ".format(hour)

    def _minutes(minute):
        return "{} minutes, ".format(minute) if minute > 1 else "{} minute, ".format(minute)

    def _seconds(second):
        return "{} seconds".format(second) if second > 1 else "{} second".format(second)

    days = seconds // (3600 * 24)
    hours = (seconds // 3600) % 24
    minutes = (seconds // 60) % 60
    seconds %= 60
    if days > 0:
        return _days(days) + _hours(hours) + _minutes(minutes) + _seconds(seconds)
    if hours > 0:
        return _hours(hours) + _minutes(minutes) + _seconds(seconds)
    if minutes > 0:
        return _minutes(minutes) + _seconds(seconds)
    return _seconds(seconds)
