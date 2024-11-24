from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Annotated
from uuid import UUID

import pydantic as pd

from dto.transaction_detail_dto import TransactionDetailDTO
from dto.transaction_split_dto import TransactionSplitDTO
from models.transaction_detail_model import TransactionDetailModel
from models.transaction_model import TransactionModel
from models.transaction_splits import TransactionSplitModel


class TransactionDTO(pd.BaseModel):
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    creditors: List[TransactionDetailDTO]
    debtors: List[TransactionDetailDTO]

    @classmethod
    def from_model(cls, model: TransactionModel) -> TransactionDTO:
        details = [
            TransactionDetailDTO.from_model(x)
            for x in TransactionDetailModel.select()
            .where(TransactionDetailModel.transaction == model.uuid)
            .iterator()
        ]
        creditors = [x for x in details if x.is_creditor]
        debtors = [x for x in details if not x.is_creditor]

        return cls(
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            creditors=creditors,
            debtors=debtors,
        )

    @classmethod
    def from_uuid(cls, uuid: UUID) -> TransactionDTO:
        return cls.from_model(TransactionModel.get_by_id(uuid))


class PersonAmountPairDTO(pd.BaseModel):
    person: pd.UUID4
    amount: Annotated[Decimal, pd.Field(default=None, ge=0, decimal_places=2)]


class CreateTransactionDTO(pd.BaseModel):
    group: pd.UUID4
    description: Optional[str]
    creditors: List[PersonAmountPairDTO]
    debtors: List[PersonAmountPairDTO]
    created_at: datetime

    @pd.model_validator(mode="after")
    def validate_amounts(self):
        total_credit = sum([creditor.amount for creditor in self.creditors])
        total_debt = sum([debtor.amount for debtor in self.debtors])
        if total_credit != total_debt:
            raise ValueError("Total credit and debt amounts do not match.")
        if total_credit <= 0:
            raise ValueError("Total credit and debt amounts cannot be zero.")
        return self
