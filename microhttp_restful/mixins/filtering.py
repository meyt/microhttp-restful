from sqlalchemy import between

from nanohttp import context, HttpBadRequest


class FilteringMixin:
    @classmethod
    def filter_by_request(cls, query=None):
        # noinspection PyUnresolvedReferences
        query = query or cls.query

        # noinspection PyUnresolvedReferences
        for c in cls.iter_dict_columns():
            # noinspection PyUnresolvedReferences
            json_name = cls.get_dict_key(c)
            if json_name in context.query_string:
                value = context.query_string[json_name]
                query = cls._filter_by_column_value(query, c, value)

        return query

    @classmethod
    def _filter_by_column_value(cls, query, column, value):
        import_value = getattr(cls, 'import_value')
        if not isinstance(value, str):
            raise HttpBadRequest()

        if value.startswith('^') or value.startswith('!^'):
            value = value.split(',')
            not_ = value[0].startswith('!^')
            first_item = value[0][2 if not_ else 1:]
            items = [first_item] + value[1:]
            items = [i for i in items if i.strip()]
            if not len(items):
                raise HttpBadRequest('Invalid query string: %s' % value)
            expression = column.in_([import_value(column, j) for j in items])
            if not_:
                expression = ~expression

        elif value.startswith('~'):
            values = value[1:].split(',')
            start, end = [import_value(column, v) for v in values]
            expression = between(column, start, end)

        elif value == 'null':
            expression = column.is_(None)
        elif value == '!null':
            expression = column.isnot(None)
        elif value.startswith('!'):
            expression = column != import_value(column, value[1:])
        elif value.startswith('>='):
            expression = column >= import_value(column, value[2:])
        elif value.startswith('>'):
            expression = column > import_value(column, value[1:])
        elif value.startswith('<='):
            expression = column <= import_value(column, value[2:])
        elif value.startswith('<'):
            expression = column < import_value(column, value[1:])
        elif value.startswith('%~'):
            expression = column.ilike('%%%s%%' % import_value(column, value[2:]))
        elif value.startswith('%'):
            expression = column.like('%%%s%%' % import_value(column, value[1:]))
        else:
            expression = column == import_value(column, value)

        return query.filter(expression)
