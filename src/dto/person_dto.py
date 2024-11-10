from __future__ import annotations

from typing import Optional
from uuid import UUID

import pydantic as pd

from models.person_model import PersonModel


class PersonCurrentDTO(pd.BaseModel):
    uuid: pd.UUID4
    email: pd.EmailStr
    username: str
    name: str
    invite_id: str

    @classmethod
    def from_model(cls, model: PersonModel) -> PersonCurrentDTO:
        return cls(
            uuid=str(model.uuid),
            email=model.email,
            username=model.username,
            name=model.name,
            invite_id=model.invite_id,
        )


class PersonUpdateDTO(pd.BaseModel):
    name: Optional[str]
    invite_id: Optional[str]


class PersonPublicDTO(pd.BaseModel):
    uuid: str
    username: str
    name: str

    @classmethod
    def from_model(cls, model: PersonModel) -> PersonPublicDTO:
        return cls(
            uuid=str(model.uuid),
            username=model.username,
            name=model.name,
        )

    @classmethod
    def from_uuid(cls, uuid: UUID) -> PersonPublicDTO:
        return cls.from_model(PersonModel.get_by_id(uuid))


class PersonRegisterDTO(pd.BaseModel):
    email: pd.EmailStr
    password: str
    username: str
    name: str


class PersonLoginDTO(pd.BaseModel):
    email: pd.EmailStr = "ybhaw@test.com"
    password: str = "password"
