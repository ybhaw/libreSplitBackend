from __future__ import annotations

from typing import Any, List
from uuid import UUID

import litestar as ls
import peewee as pw
from litestar.exceptions import ValidationException
from litestar.security.jwt import Token

from dto.group_dto import GroupDTO, GroupCreateDTO, GroupByMembersDTO, GroupUpdateDTO
from models.group_model import GroupModel
from models.group_member_model import GroupMemberModel
from models.person_model import PersonModel


class GroupController(ls.Controller):
    path = "/group"
    tags = ["Group"]

    async def _get_by_id(self, group_id: UUID) -> GroupDTO:
        group = GroupModel.select().where(GroupModel.uuid == group_id).first()
        return GroupDTO.from_model(group)

    async def _create_group(self, group_data: GroupCreateDTO) -> GroupDTO:
        print("Group data", group_data)
        group = GroupModel.create(
            name=group_data.name,
            description=group_data.description,
        )
        group.save()
        for member in group_data.members:
            GroupMemberModel.create(
                group=group.uuid,
                person=member,
            ).save()
        return GroupDTO.from_model(group)

    async def _update_group(self, group_data: GroupUpdateDTO) -> GroupDTO:
        group = GroupModel.select().where(GroupModel.uuid == group_data.uuid).first()
        if not group:
            raise ValidationException("Group not found.")
        if group_data.name:
            group.name = group_data.name
        if group_data.description:
            group.description = group_data.description
        group.save()
        if group_data.membersToAdd:
            existing_members = list(
                GroupMemberModel.select(GroupMemberModel.person)
                .where(
                    GroupMemberModel.group == group.uuid
                    and GroupMemberModel.person.in_(group_data.membersToAdd)
                )
                .iterator()
            )
            for member in group_data.membersToAdd:
                if member not in existing_members:
                    GroupMemberModel.create(
                        group=group.uuid,
                        person=member,
                    ).save()
        return GroupDTO.from_model(group)

    @ls.post()
    async def create(self, data: GroupCreateDTO) -> GroupDTO:
        return await self._create_group(data)

    @ls.patch()
    async def update(self, data: GroupUpdateDTO) -> GroupDTO:
        return await self._update_group(data)

    @ls.get()
    async def get(self, request: ls.Request[PersonModel, Token, Any]) -> List[GroupDTO]:
        person = request.user
        group_ids = [
            x.group_id
            for x in GroupMemberModel.select(GroupMemberModel.group)
            .where(GroupMemberModel.person == person.uuid)
            .iterator()
        ]
        return [await self._get_by_id(group_id) for group_id in group_ids]

    @ls.post("/members")
    async def get_by_members(
        self, request: ls.Request[PersonModel, Token, Any], data: GroupByMembersDTO
    ) -> GroupDTO:
        user = request.user
        all_members = [user.uuid, *data.members]
        group_members = (
            GroupMemberModel.select(GroupMemberModel.group)
            .where(GroupMemberModel.person.in_(all_members))
            .group_by(GroupMemberModel.group)
            .having(pw.fn.Count(GroupMemberModel.person) == len(all_members))
            .order_by(GroupMemberModel.created_at)
        )
        valid_groups = (
            GroupMemberModel.select(GroupMemberModel.group)
            .where(GroupMemberModel.group.in_(group_members))
            .group_by(GroupMemberModel.group)
            .having(pw.fn.Count(GroupMemberModel.person) == len(all_members))
            .order_by(GroupMemberModel.created_at)
        )
        group_ids = [x.group_id for x in valid_groups.iterator()]
        for group_id in group_ids:
            if (
                GroupModel.select()
                .where(GroupModel.uuid == group_id and GroupModel.name.is_null())
                .exists()
            ):
                return await self._get_by_id(group_id)
        dto = GroupCreateDTO(
            name=None,
            description=None,
            members=all_members,
        )
        return await self._create_group(dto)

    @ls.post("/add-member")
    async def add_member(self, group_id: UUID, person_id: UUID) -> GroupDTO:
        if not GroupModel.select().where(GroupModel.uuid == group_id).exists():
            raise ValidationException("Group not found.")
        if (
            GroupMemberModel.select()
            .where(
                GroupMemberModel.group == group_id
                and GroupMemberModel.person == person_id
            )
            .exists()
        ):
            raise ValidationException("Person already in group.")
        GroupMemberModel.create(
            group=group_id,
            person=person_id,
        ).save()
        return self._get_by_id(group_id)
