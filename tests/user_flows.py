from uuid import UUID

import argon2

from database import db, delete_db
from models.group_member_model import GroupMemberModel
from models.group_model import GroupModel
from models.person_model import PersonModel
from models.transaction_detail_model import TransactionDetailModel
from models.transaction_model import TransactionModel
from models.transaction_splits import TransactionSplitModel


def clear_database():
    delete_db()
    db.connect()
    db.create_tables(
        [
            PersonModel,
            GroupModel,
            GroupMemberModel,
            TransactionModel,
            TransactionDetailModel,
            TransactionSplitModel,
        ]
    )


def create_people():
    person_1 = PersonModel.create(
        uuid=UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
        email="ybhaw@test.com",
        password=argon2.PasswordHasher().hash("password"),
        username="ybhaw",
        name="Vaibhaw Kumar",
        invite_id="00000",
    )
    person_1.save()

    person_2 = PersonModel.create(
        uuid=UUID("86ac4fa7-ff38-4ae4-8c85-0d4546f28f43"),
        email="person2@test.com",
        password=argon2.PasswordHasher().hash("password"),
        username="person2",
        name="John Doe",
        invite_id="00000",
    )
    person_2.save()

    person_3 = PersonModel.create(
        uuid=UUID("5c799b35-70ae-4d75-8236-0a407e91ac57"),
        email="person3@test.com",
        password=argon2.PasswordHasher().hash("password"),
        username="person3",
        name="Jack Sparrow",
        invite_id="00000",
    )
    person_3.save()

    person_4 = PersonModel.create(
        uuid=UUID("d25da9ac-6dc6-466d-8f50-8cd769f17651"),
        email="person4@test.com",
        password=argon2.PasswordHasher().hash("password"),
        username="person4",
        name="Alice Marry",
        invite_id="00000",
    )
    person_4.save()


def main_process():
    clear_database()
    create_people()


if __name__ == "__main__":
    main_process()
