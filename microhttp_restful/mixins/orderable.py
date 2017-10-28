
from sqlalchemy import Integer

from microhttp_restful import Field


class OrderableMixin:
    order = Field("order", Integer, default=0, nullable=False)
    __mapper_args__ = dict(order_by=order)

    @classmethod
    def apply_default_sort(cls, query=None):
        # noinspection PyUnresolvedReferences
        return (query or cls.query).order_by(cls.order)
