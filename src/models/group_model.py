from __future__ import annotations

from uuid import uuid4

import peewee as pw

from database import db
from utility import utcnow


class GroupModel(pw.Model):
    uuid = pw.UUIDField(unique=True, index=True, primary_key=True, default=uuid4)
    name = pw.CharField(max_length=400, null=True, default=None)
    description = pw.CharField(max_length=1000, null=True, default=None)
    created_at = pw.DateTimeField(default=utcnow)
    updated_at = pw.DateTimeField(default=utcnow, index=True)

    class Meta:
        database = db
