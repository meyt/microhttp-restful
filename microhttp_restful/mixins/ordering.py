from sqlalchemy import desc

from nanohttp import context


class OrderingMixin:

    @classmethod
    def _sort_by_key_value(cls, query, column, descending=False):
        expression = column

        if column.info.get('collation'):
            expression = expression.collate(column.info['collation'])

        if descending:
            expression = desc(expression)

        return query.order_by(expression)

    @classmethod
    def sort_by_request(cls, query=None):
        # noinspection PyUnresolvedReferences
        query = query or cls.query

        sort_exp = context.query.get('sort', '').strip()
        if not sort_exp:
            return query

        sort_columns = [
            (c[1:] if c.startswith('-') else c, c.startswith('-'))
            for c in sort_exp.split(',')
        ]

        # noinspection PyUnresolvedReferences
        criteria = cls.create_sort_criteria(sort_columns)

        for criterion in criteria:
            query = cls._sort_by_key_value(query, *criterion)

        return query
