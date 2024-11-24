import os

from peewee import SqliteDatabase

os.makedirs("/tmp/db", exist_ok=True)
db = SqliteDatabase("/tmp/db/libreSplit.db")


def delete_db():
    os.system("rm /tmp/db/libreSplit.db")
