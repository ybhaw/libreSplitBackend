from __future__ import annotations

import random
from uuid import uuid4

import peewee as pw

from database import db
from utility import utcnow


def create_invite_id():
    return str(random.randint(100, 999)).zfill(5)


class PersonModel(pw.Model):
    uuid = pw.UUIDField(
        unique=True,
        index=True,
        primary_key=True,
        default=uuid4,
    )
    email = pw.CharField(max_length=400, null=False, index=True)
    password = pw.CharField(max_length=1000, null=False)
    username = pw.CharField(max_length=20, null=False, index=True)
    name = pw.CharField(max_length=400, null=False, index=True)
    invite_id = pw.CharField(max_length=10, null=False, default=create_invite_id)
    created_at = pw.DateTimeField(default=utcnow, null=False, index=True)
    updated_at = pw.DateTimeField(default=utcnow, null=False, index=True)

    class Meta:
        database = db
