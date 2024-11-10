from uuid import uuid4

import peewee as pw
from database import db
from models.group_model import GroupModel
from utility import utcnow


class TransactionModel(pw.Model):
    uuid = pw.UUIDField(
        unique=True,
        index=True,
        primary_key=True,
        default=uuid4,
    )
    group = pw.ForeignKeyField(GroupModel, backref="transactions", index=True)
    description = pw.CharField(max_length=400, null=True)
    created_at = pw.DateTimeField(default=utcnow)
    updated_at = pw.DateTimeField(default=utcnow)

    class Meta:
        database = db
