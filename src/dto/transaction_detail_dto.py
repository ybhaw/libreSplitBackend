from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, Annotated
from uuid import UUID

import pydantic as pd

from dto.person_dto import PersonPublicDTO
from models.transaction_detail_model import TransactionDetailModel


class TransactionDetailDTO(pd.BaseModel):
    uuid: UUID
    person: PersonPublicDTO
    amount: Annotated[Decimal, pd.Field(default=None, ge=0, decimal_places=2)]
    is_creditor: bool
    updated_at: datetime

    @classmethod
    def from_model(cls, model: TransactionDetailModel) -> TransactionDetailDTO:
        model = cls(
            uuid=model.uuid,
            person=PersonPublicDTO.from_uuid(model.person),
            amount=model.amount,
            is_creditor=model.is_creditor,
            updated_at=model.updated_at,
        )
        return model

    @classmethod
    def from_uuid(cls, uuid: UUID) -> TransactionDetailModel:
        return cls.from_model(TransactionDetailModel.get_by_id(uuid))
