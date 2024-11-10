from __future__ import annotations

from decimal import Decimal
from typing import Annotated
from uuid import UUID

import pydantic as pd

from dto.person_dto import PersonPublicDTO
from models.transaction_splits import TransactionSplitModel


class TransactionSplitDTO(pd.BaseModel):
    uuid: UUID
    person: PersonPublicDTO
    is_creditor: bool
    amount: Annotated[Decimal, pd.Field(default=None, ge=0, decimal_places=2)]

    @classmethod
    def from_model(cls, model: TransactionSplitModel) -> TransactionSplitModel:
        model = cls(
            uuid=model.uuid,
            person=PersonPublicDTO.from_uuid(model.person),
            is_creditor=model.is_creditor,
            amount=model.amount,
        )
        return model

    @classmethod
    def from_uuid(cls, uuid: UUID) -> TransactionSplitModel:
        return cls.from_model(TransactionSplitModel.get_by_id(uuid))
