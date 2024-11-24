from __future__ import annotations

import litestar as ls
from litestar.exceptions import ValidationException

from dto.group_dto import GroupDTO
from dto.transaction_dto import CreateTransactionDTO, TransactionDTO
from models.transaction_detail_model import TransactionDetailModel
from models.transaction_model import TransactionModel


class TransactionController(ls.Controller):
    path = "/transaction"
    tags = ["Transaction"]

    async def _create_transaction(self, data: CreateTransactionDTO) -> GroupDTO:
        transaction = TransactionModel.create(
            description=data.description,
            group=str(data.group),
        )
        transaction.save()
        credit_sum = sum([x.amount for x in data.creditors])
        debt_sum = sum([x.amount for x in data.debtors])
        if credit_sum != debt_sum:
            raise ValidationException("Credit and debt amounts do not match.")
        for creditor in data.creditors:
            TransactionDetailModel.create(
                transaction=transaction.uuid,
                person=creditor.person,
                amount=creditor.amount,
                is_creditor=True,
            ).save()
        for debtor in data.debtors:
            TransactionDetailModel.create(
                transaction=transaction.uuid,
                person=debtor.person,
                amount=debtor.amount,
                is_creditor=False,
            ).save()

        return GroupDTO.from_uuid(data.group)

    @ls.post()
    async def create_transaction(self, data: CreateTransactionDTO) -> TransactionDTO:
        return await self._create_transaction(data)
