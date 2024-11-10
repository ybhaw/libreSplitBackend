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
    creditor = pw.ForeignKeyField(PersonModel, backref="creditor", index=True)
    debtor = pw.ForeignKeyField(PersonModel, backref="debtor", index=True)
    amount = pw.DecimalField(decimal_places=2, auto_round=True)
    created_at = pw.DateTimeField(default=utcnow)
    updated_at = pw.DateTimeField(default=utcnow)
    settled_at = pw.DateTimeField(null=True, default=None, index=True)

    class Meta:
        database = db
