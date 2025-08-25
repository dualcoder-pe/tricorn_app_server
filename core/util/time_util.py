from datetime import datetime


def today(splitter: str = "-") -> str:
    return datetime.now().strftime(f"%Y{splitter}%m{splitter}%d")


def this_month():
    return datetime.now().strftime('%Y-%m')


def current_time_second():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


def convert_ymd_date_to_timestamp(date):
    return int(datetime.strptime(date, "%Y-%m-%d").timestamp())


def convert_ymd_date_to_datetime(date):
    return datetime.strptime(date, "%Y-%m-%d")
