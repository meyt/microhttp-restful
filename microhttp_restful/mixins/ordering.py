from sqlalchemy import desc
from sqlalchemy.sql.expression import nullslast, nullsfirst

from nanohttp import context

from microhttp_restful.mixins import OrderableMixin


class OrderingMixin:
    __order_with_nulls__ = True  # set it False for sqlite

    @classmethod
    def _sort_by_key_value(cls, query, column, descending=False):
        expression = column

        if descending:
            expression = desc(expression)

        if cls.__order_with_nulls__:
            return query.order_by((nullsfirst if descending else nullslast)(expression))

        return query.order_by(expression)

    @classmethod
    def sort_by_request(cls, query=None):
        # noinspection PyUnresolvedReferences
        query = query or cls.query

        sort_exp = context.query_string.get('sort', '').strip()
        if not sort_exp:
            if issubclass(cls, OrderableMixin):
                # noinspection PyUnresolvedReferences
                return cls.apply_default_sort(query)
            return query

        sort_columns = {c[1:] if c.startswith('-') else c: 'desc' if c.startswith('-') else 'asc'
                        for c in sort_exp.split(',')}

        # noinspection PyUnresolvedReferences
        criteria = cls.create_sort_criteria(sort_columns)

        for criterion in criteria:
            query = cls._sort_by_key_value(query, *criterion)

        return query
