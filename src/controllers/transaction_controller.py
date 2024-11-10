from __future__ import annotations

from decimal import Decimal
from uuid import UUID

import litestar as ls

from dto.group_dto import GroupDTO
from dto.transaction_dto import CreateTransactionDTO, TransactionDTO
from models.transaction_detail_model import TransactionDetailModel
from models.transaction_model import TransactionModel
from models.transaction_splits import TransactionSplitModel
from utility import utcnow


class TransactionController(ls.Controller):
    path = "/transaction"
    tags = ["Transaction"]

    async def _create_transaction(self, data: CreateTransactionDTO) -> GroupDTO:
        people = {}
        for creditor in data.creditors:
            people[creditor.person] = people.get(creditor.person, 0) + creditor.amount
        for debtor in data.debtors:
            people[debtor.person] = people.get(debtor.person, 0) - debtor.amount
        creditors = sorted([[a, p] for p, a in people.items() if a > 0])
        debtors = sorted([[a, p] for p, a in people.items() if a < 0], reverse=True)

        details = await self._build_details(creditors, debtors)

        transaction = TransactionModel.create(
            description=data.description,
            group=str(data.group),
        )
        transaction.save()

        for d in details:
            TransactionDetailModel.create(
                creditor=d[0],
                debtors=d[1],
                amount=d[2],
                transaction=transaction.uuid,
            ).save()

        for c in data.creditors:
            TransactionSplitModel.create(
                person=c.person,
                amount=c.amount,
                is_creditor=True,
                transaction=transaction.uuid,
            ).save()

        for d in data.debtors:
            TransactionSplitModel.create(
                person=d.person,
                amount=d.amount,
                is_creditor=False,
                transaction=transaction.uuid,
            ).save()

        return GroupDTO.from_uuid(data.group)

    async def _build_details(self, creditors, debtors):
        if len(creditors) == 0 or len(debtors) == 0:
            return []
        details = []
        c = creditors.pop()
        d = debtors.pop()
        while len(creditors) > 0 and len(debtors) > 0:
            if c[0] > d[0]:
                # Creditor has more money
                details.append((c[1], d[1], d[0]))
                c[0] = c[0] - d[0]
                d[0] = 0
            else:
                # Debtor has more or same money
                details.append((c[1], d[1], c[0]))
                d[0] = d[0] - c[0]
                c[0] = 0
            if d[0] <= 0:
                d = debtors.pop()
            if c[0] <= 0:
                c = creditors.pop()
        if len(creditors) > 0:
            while len(creditors) > 0:
                if c[0] > d[0]:
                    raise ValueError("Hmm, something unexpected happened!")
                details.append((c[1], d[1], c[0]))
                d[0] = d[0] - c[0]
                c = creditors.pop()
        elif len(debtors) > 0:
            while len(debtors) > 0:
                if c[0] > d[0]:
                    raise ValueError("Hmm, something unexpected happened!")
                details.append((c[1], d[1], d[0]))
                c[0] = c[0] - d[0]
                d = debtors.pop()
        if Decimal(c[0]).quantize("0.01") != Decimal(d[0]).quantize("0.01"):
            raise ValueError("Hmm, something unexpected happened!")
        details.append((c[1], d[1], c[0]))
        return details

    @ls.post()
    async def create_transaction(self, data: CreateTransactionDTO) -> TransactionDTO:
        return await self._create_transaction(data)

    @ls.post("/settle")
    async def settle_transaction(
        self, request: ls.Request, transaction_detail_id: UUID
    ) -> GroupDTO:
        current_user = request.user.uuid
        transaction_detail: TransactionDetailModel = TransactionDetailModel.get_by_id(
            transaction_detail_id
        )
        print(current_user, transaction_detail.creditor, transaction_detail.debtor)
        if (
            transaction_detail.creditor.uuid != current_user
            and transaction_detail.debtor.uuid != current_user
        ):
            raise ValueError("You are not part of this transaction.")
        if transaction_detail.settled_at:
            raise ValueError("Transaction already settled.")
        transaction_detail.settled_at = utcnow()
        transaction_detail.save()
        transaction_group = TransactionModel.get_by_id(
            transaction_detail.transaction
        ).group
        return GroupDTO.from_uuid(transaction_group)
