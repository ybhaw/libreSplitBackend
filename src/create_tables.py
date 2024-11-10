from typing import List
from uuid import UUID

import argon2
import faker

from database import db, delete_db
from models.group_member_model import GroupMemberModel
from models.group_model import GroupModel
from models.person_model import PersonModel
from models.transaction_detail_model import TransactionDetailModel
from models.transaction_model import TransactionModel
from models.transaction_splits import TransactionSplitModel

f = faker.Faker()


def main():
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
    user = create_active_user()
    people = create_people(f.random_int(10, 20))
    groups = create_groups(user, people, f.random_int(2, 8))
    create_transactions(groups)
    db.close()


def create_active_user():
    user_uuid = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    email = "ybhaw@test.com"
    name = "Vaibhaw"
    username = "ybhaw"
    password = "password"
    person = PersonModel.create(
        uuid=UUID(user_uuid),
        email=email,
        password=argon2.PasswordHasher().hash(password),
        username=username,
        name=name,
        invite_id="00000",
    )
    person.save()
    return person


def create_people(count: int):
    saved_people = []
    for i in range(count):
        person = PersonModel.create(
            email=f.email(),
            password=argon2.PasswordHasher().hash("password"),
            username=f.user_name(),
            name=f.name(),
            invite_id="0000",
        )
        person.save()
        saved_people.append(person)
    return saved_people


def create_groups(user: PersonModel, people: List[PersonModel], group_count: int):
    created_groups = []
    group = GroupModel.create(
        uuid=UUID("7426c474-335f-48c9-8109-77f33e090ff9"), name="My Transaction"
    )
    group.save()
    GroupMemberModel.create(
        group=group.uuid,
        person=user.uuid,
    ).save()
    created_groups.append(group)

    for i in range(group_count):
        sample = f.random_sample(people, length=f.random_int(2, min(8, len(people))))
        group = GroupModel.create(
            name=f.street_name(),
            description=f.text(max_nb_chars=400) if f.random_int() % 2 == 0 else None,
        )
        group.save()
        GroupMemberModel.create(
            group=group.uuid,
            person=user.uuid,
        ).save()
        for person in sample:
            GroupMemberModel.create(
                group=group.uuid,
                person=person.uuid,
            ).save()
        created_groups.append(group)
    return created_groups


def create_transactions(groups: List[GroupModel]):
    for group in groups:
        members = [
            x.person.uuid
            for x in list(
                GroupMemberModel.select(GroupMemberModel.person)
                .where(GroupMemberModel.group == group.uuid)
                .iterator()
            )
        ]
        n = len(members)
        max_possible_permutation_pairs = int(n * (n - 1) / 2) + n

        for i in range(0, f.random_int(2, 10)):
            transaction = TransactionModel.create(
                group=group.uuid, description=f.text(20)
            )
            details_pairs = {}
            for d in range(1, f.random_int(max(max_possible_permutation_pairs, 5))):
                creditor = f.random_element(members)

                debtor = f.random_element(members)
                pair = details_pairs.get(creditor, {})
                pair[debtor] = f.random_int(1, 100000) / 100
                details_pairs[creditor] = pair
            transaction.save()
            for creditor in details_pairs:
                for debtor in details_pairs[creditor]:
                    transaction_detail = TransactionDetailModel.create(
                        transaction=transaction.uuid,
                        creditor=creditor,
                        debtor=debtor,
                        amount=details_pairs[creditor][debtor],
                    )
                    transaction_detail.save()


if __name__ == "__main__":
    main()
