import os
from typing import Optional
from uuid import UUID
from dotenv import load_dotenv

import litestar as ls
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from litestar.exceptions import ValidationException
from litestar.security.jwt import JWTAuth, Token

from dto.person_dto import PersonCurrentDTO, PersonRegisterDTO, PersonLoginDTO
from models.person_model import PersonModel


async def get_logged_in_user(token: Token, _) -> Optional[PersonModel]:
    return PersonCurrentDTO.from_model(
        PersonModel.select().where(PersonModel.uuid == UUID(token.sub)).first()
    )


load_dotenv()

jwt_auth = JWTAuth[PersonCurrentDTO](
    retrieve_user_handler=get_logged_in_user,
    token_secret=os.getenv("TOKEN_SECRET"),
    exclude=["/login", "/register", "/schema"],
)


class AuthenticationController(ls.Controller):

    tags = ["Authentication"]

    @ls.post("/login")
    async def login(self, data: PersonLoginDTO) -> ls.Response[PersonCurrentDTO]:
        person = PersonModel.select().where(PersonModel.email == data.email).first()
        if not person:
            # TODO: Make this generic
            raise ValidationException("Email not found.")
        ph = PasswordHasher()
        try:
            ph.verify(person.password, data.password)
        except VerifyMismatchError:
            raise ValidationException("Password incorrect.")
        except Exception as e:
            raise e
        return ls.Response(
            PersonCurrentDTO.from_model(person),
            headers={
                "Authorization": "Bearer " + jwt_auth.create_token(str(person.uuid))
            },
        )

    @ls.post("/register")
    async def register(self, data: PersonRegisterDTO) -> PersonCurrentDTO:
        person = PersonModel.select().where(
            PersonModel.email == data.email or PersonModel.username == data.username
        )
        if person.exists():
            # TODO: Make this generic
            raise ValidationException("Email or Username already exists.")
        ph = PasswordHasher()
        person = PersonModel.create(
            email=data.email,
            password=ph.hash(data.password),
            username=data.username,
            name=data.name,
        )
        person.save()
        return PersonCurrentDTO.from_model(person)
