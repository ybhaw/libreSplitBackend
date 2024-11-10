from __future__ import annotations

from typing import Any
from uuid import UUID

import litestar as ls
from litestar import Request
from litestar.exceptions import ValidationException
from litestar.security.jwt import Token

from dto.person_dto import PersonCurrentDTO, PersonUpdateDTO, PersonPublicDTO
from models.person_model import PersonModel


class PersonController(ls.Controller):
    path = "/person"
    tags = ["Person"]

    @ls.get()
    async def get_me(
        self, request: Request[PersonModel, Token, Any]
    ) -> PersonCurrentDTO:
        return PersonCurrentDTO.from_model(request.user)

    @ls.get("/username/{username:str}/invite-id/{invite_id:str}")
    async def get_by_username_invite_id(
        self, username: str, invite_id: str
    ) -> PersonPublicDTO:
        person = (
            PersonModel.select()
            .where(
                (PersonModel.username == username)
                & (PersonModel.invite_id == invite_id)
            )
            .first()
        )
        if not person:
            raise ValidationException("Person not found!")
        return PersonPublicDTO.from_model(person)

    @ls.get("/uuid/{uuid:str}")
    async def get_by_uuid(self, uuid: str) -> PersonPublicDTO:
        person = PersonModel.get_or_none(PersonModel.uuid == UUID(uuid))
        if not person:
            raise ValidationException("Person not found!")
        return PersonPublicDTO.from_model(person)

    @ls.patch()
    async def update_me(
        self, request: ls.Request, data: PersonUpdateDTO
    ) -> PersonCurrentDTO:
        person = PersonModel.get_by_id(request.user.uuid)
        if data.name:
            person.name = data.name
        if data.invite_id:
            person.invite_id = data.invite_id
        person.save()
        return PersonCurrentDTO.from_model(person)
