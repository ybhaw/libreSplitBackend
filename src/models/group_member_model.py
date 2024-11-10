from __future__ import annotations

from uuid import uuid4

import peewee as pw

from database import db
from models.group_model import GroupModel
from models.person_model import PersonModel
from utility import utcnow


class GroupMemberModel(pw.Model):
    uuid = pw.CharField(
        max_length=400, unique=True, index=True, primary_key=True, default=uuid4
    )
    person = pw.ForeignKeyField(PersonModel, backref="groups", index=True)
    group = pw.ForeignKeyField(GroupModel, backref="members", index=True)
    created_at = pw.DateTimeField(default=utcnow)
    updated_at = pw.DateTimeField(default=utcnow)

    class Meta:
        database = db
