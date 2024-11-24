from uuid import uuid4

import peewee as pw
from database import db
from models.person_model import PersonModel
from models.transaction_model import TransactionModel
from utility import utcnow


class TransactionDetailModel(pw.Model):
    uuid = pw.UUIDField(
        unique=True,
        index=True,
        primary_key=True,
        default=uuid4,
    )
    transaction = pw.ForeignKeyField(TransactionModel, backref="details", index=True)
    person = pw.ForeignKeyField(PersonModel, backref="person", index=True)
    amount = pw.DecimalField(decimal_places=2, auto_round=True)
    is_creditor = pw.BooleanField(default=False, index=True)
    created_at = pw.DateTimeField(default=utcnow)
    updated_at = pw.DateTimeField(default=utcnow)

    class Meta:
        database = db
