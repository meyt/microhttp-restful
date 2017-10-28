from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.ext.hybrid import hybrid_property

from microhttp_restful import Field


class ActivationMixin:
    activated_at = Field(DateTime, nullable=True, readonly=True, protected=True)

    @hybrid_property
    def is_active(self):
        return self.activated_at is not None

    @is_active.setter
    def is_active(self, value):
        self.activated_at = datetime.now() if value else None

    # noinspection PyUnresolvedReferences
    @is_active.expression
    def is_active(self):
        # noinspection PyUnresolvedReferences
        return self.activated_at.isnot(None)

    @classmethod
    def filter_activated(cls, query=None):
        # noinspection PyUnresolvedReferences
        # noinspection PyPropertyAccess
        return (query or cls.query).filter(cls.is_active)

    @classmethod
    def import_value(cls, column, v):
        # noinspection PyUnresolvedReferences
        # noinspection PyPropertyAccess
        if column.key == cls.is_active.key and not isinstance(v, bool):
            return str(v).lower() == 'true'
        # noinspection PyUnresolvedReferences
        return super().import_value(column, v)
