import os
import datetime


def get_relative_path(*paths: str):
    return os.path.join(os.path.dirname(__file__), "..", *paths)


def utcnow():
    return datetime.datetime.now(tz=datetime.timezone.utc)
