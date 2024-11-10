from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, Annotated
from uuid import UUID

import pydantic as pd

from dto.person_dto import PersonPublicDTO
from models.transaction_detail_model import TransactionDetailModel
from utility import utcnow


class TransactionDetailDTO(pd.BaseModel):
    uuid: UUID
    creditor: PersonPublicDTO
    debtor: PersonPublicDTO
    amount: Annotated[Decimal, pd.Field(default=None, ge=0, decimal_places=2)]
    updated_at: datetime
    settled_at: Optional[datetime]

    @classmethod
    def from_model(cls, model: TransactionDetailModel) -> TransactionDetailDTO:
        model = cls(
            uuid=model.uuid,
            creditor=PersonPublicDTO.from_uuid(model.creditor),
            debtor=PersonPublicDTO.from_uuid(model.debtor),
            amount=model.amount,
            updated_at=model.updated_at,
            settled_at=model.settled_at,
        )
        return model

    @classmethod
    def from_uuid(cls, uuid: UUID) -> TransactionDetailModel:
        return cls.from_model(TransactionDetailModel.get_by_id(uuid))


class TransactionDetailInternalDTO(pd.BaseModel):
    creditor: UUID
    debtor: UUID
    amount: Annotated[Decimal, pd.Field(default=None, ge=0, decimal_places=2)]
    created_at: datetime = pd.Field(default_factory=utcnow)
    updated_at: datetime = pd.Field(default_factory=utcnow)
