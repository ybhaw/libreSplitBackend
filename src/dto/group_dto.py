from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import UUID

import pydantic as pd

from dto.person_dto import PersonPublicDTO
from dto.transaction_dto import TransactionDTO
from models.group_member_model import GroupMemberModel
from models.group_model import GroupModel
from models.person_model import PersonModel
from models.transaction_model import TransactionModel


class GroupDTO(pd.BaseModel):
    uuid: pd.UUID4
    name: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    members: List[PersonPublicDTO]
    transactions: List[TransactionDTO]

    @classmethod
    def from_model(cls, group: GroupModel) -> GroupDTO:
        group_members = GroupMemberModel.select(GroupMemberModel.person).where(
            GroupMemberModel.group == group
        )
        people = PersonModel.select().where(PersonModel.uuid.in_(group_members))
        transactions = TransactionModel.select().where(
            TransactionModel.group == group.uuid
        )
        return cls(
            uuid=group.uuid,
            name=group.name,
            description=group.description,
            created_at=group.created_at,
            updated_at=group.updated_at,
            members=[
                PersonPublicDTO.from_model(person) for person in people.iterator()
            ],
            transactions=[
                TransactionDTO.from_model(transaction) for transaction in transactions
            ],
        )

    @classmethod
    def from_uuid(cls, uuid: UUID) -> GroupDTO:
        group = GroupModel.get_by_id(uuid)
        return cls.from_model(group)


class GroupCreateDTO(pd.BaseModel):
    name: Optional[str]
    description: Optional[str]
    members: List[pd.UUID4]  # List of person uuids

    @pd.field_validator("members")
    @classmethod
    def check_members(cls, members):
        if len(members) == 0:
            raise ValueError("Members cannot be empty.")
        member_count = PersonModel.select().where(PersonModel.uuid.in_(members)).count()
        if member_count != len(members):
            raise ValueError("Some members do not exist.")
        return members


class GroupUpdateDTO(pd.BaseModel):
    uuid: str
    name: Optional[str]
    description: Optional[str]
    membersToAdd: Optional[List[pd.UUID4]]  # List of person uuids


class GroupByMembersDTO(pd.BaseModel):
    members: List[pd.UUID4]

    @pd.field_validator("members")
    @classmethod
    def check_members(cls, members):
        if len(members) == 0:
            return []
        member_count = PersonModel.select().where(PersonModel.uuid.in_(members)).count()
        if member_count != len(members):
            raise ValueError("Some members do not exist.")
        return members
