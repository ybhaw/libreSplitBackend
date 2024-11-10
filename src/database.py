import os

from peewee import SqliteDatabase

from utility import get_relative_path

db = SqliteDatabase(get_relative_path("libreSplit.db"))


def delete_db():
    os.system(f"rm {get_relative_path('libreSplit.db')}")
