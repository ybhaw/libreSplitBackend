from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type

import peewee as pw

PeeweeModel = TypeVar("PeeweeModel", bound=pw.Model)


class DataclassModel(ABC, Generic[PeeweeModel]):
    @classmethod
    def from_model(cls, model: pw.Model) -> DataclassModel:
        """
        Converts a peewee model to a dataclass model.
        :param model: The peewee model to convert
        :return: The converted dataclass model
        """

    def to_model(self, model: pw.Model) -> pw.Model:
        """
        Converts a dataclass model to a peewee model.
        :param model: The peewee model to convert
        :return: The converted dataclass model
        """


DataclassModelGeneric = TypeVar("DataclassModelGeneric", bound=DataclassModel)


class Dao(ABC, Generic[PeeweeModel, DataclassModelGeneric]):
    def __init__(
        self,
        model_class: Type[PeeweeModel],
        data_class: Type[DataclassModelGeneric],
    ):
        self.model_class: Type[PeeweeModel] = model_class
        self.data_class: Type[DataclassModelGeneric] = data_class

    @abstractmethod
    def validate(self, model: DataclassModelGeneric) -> DataclassModelGeneric:
        """
        Validates the model before saving it to db.
        :param model: The model to validate
        :return: The validated model
        """

    @abstractmethod
    def create(self, model: DataclassModelGeneric) -> DataclassModelGeneric:
        """
        Creates a new model in the db.
        :param model: The model to create
        :return: The created model
        """

    @abstractmethod
    def update(self, model: DataclassModelGeneric) -> DataclassModelGeneric:
        """
        Updates an existing model in the db.
        :param model: The model to update
        :return: The updated model
        """

    @abstractmethod
    def upsert(self, model: DataclassModelGeneric) -> DataclassModelGeneric:
        """
        Updates an existing model in the db or creates a new one if it doesn't exist.
        :param model: The model to update or create
        :return: The updated or created model
        """

    @abstractmethod
    def delete(self, model: DataclassModelGeneric) -> None:
        """
        Deletes an existing model from the db.
        :param model: The model to delete
        """


class GenericDao(
    Generic[PeeweeModel, DataclassModelGeneric],
    Dao[PeeweeModel, DataclassModelGeneric],
):
    DELETE__ = object()

    def validate(self, model: DataclassModelGeneric) -> DataclassModelGeneric:
        return model

    def create(self, model: DataclassModelGeneric) -> DataclassModelGeneric:
        return self.data_class.from_model(
            self.model_class.create(**dataclasses.asdict(model))
        )

    def update(self, model: DataclassModelGeneric) -> DataclassModelGeneric:
        model = (
            self.model_class.select().where(self.model_class.uuid == model.uuid).get()
        )
        if model is None:
            raise ValueError(f"Model with uuid {model.uuid} does not exist")
        for field, value in dataclasses.asdict(model).items():
            if value is None:
                continue
            if value is self.DELETE__:
                setattr(model, field, None)
            else:
                setattr(model, field, value)
        model.save()
        return self.data_class.from_model(model)

    def upsert(self, model: DataclassModelGeneric) -> DataclassModelGeneric:
        if (
            self.model_class.select().where(self.model_class.uuid == model.uuid).first()
            is not None
        ):
            return self.update(model)
        return self.create(model)

    def delete(self, model: DataclassModelGeneric) -> None:
        model = (
            self.model_class.select().where(self.model_class.uuid == model.uuid).get()
        )
        model.delete_instance()
