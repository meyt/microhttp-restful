import functools

from sqlalchemy import event
from sqlalchemy.orm import validates
from sqlalchemy.inspection import inspect

from sqlalchemy_dict import BaseModel as SADictBaseModel

from webtest_docgen import FormParam

from nanohttp import context, HttpNotFound

from microhttp_restful import MetadataField, Field
from microhttp_restful.validation import validate_form
from microhttp_restful.mixins import PaginationMixin, FilteringMixin, OrderingMixin


# noinspection PyClassHasNoInit
class BaseModel(SADictBaseModel):

    def update_from_request(self):
        self.update_from_dict(context.form)

    @classmethod
    def iter_metadata_fields(cls):
        for c in cls.iter_dict_columns(relationships=True,
                                       include_readonly_columns=True,
                                       include_protected_columns=True):
            yield from MetadataField.from_column(cls.get_column(c),
                                                 json_name=cls.get_dict_key(c),
                                                 info=c.info)

    @classmethod
    def json_metadata(cls):
        fields = {f.json_name: f.to_json() for f in cls.iter_metadata_fields()}
        mapper = inspect(cls)
        return {
            'name': cls.__name__,
            'primaryKeys': [c.key for c in mapper.primary_key],
            'fields': fields
        }

    @classmethod
    def create_sort_criteria(cls, sort_columns):
        criteria = []
        for c in cls.iter_dict_columns():
            json_name = cls.get_dict_key(c)
            if json_name in sort_columns:
                criteria.append((c, sort_columns[json_name] == 'desc'))
        return criteria

    # noinspection PyUnresolvedReferences
    @classmethod
    def filter_paginate_sort_query_by_request(cls, query=None):
        query = query or cls.query

        if issubclass(cls, FilteringMixin):
            query = cls.filter_by_request(query)

        if issubclass(cls, OrderingMixin):
            query = cls.sort_by_request(query)

        if issubclass(cls, PaginationMixin):
            query = cls.paginate_by_request(query=query)

        return query

    @classmethod
    def dump_query(cls, query=None):
        return super().dump_query(cls.filter_paginate_sort_query_by_request(query))

    @classmethod
    def create_validation_rules(cls, **rules):
        patterns = {}
        blacklist = []
        requires = []
        for field in cls.iter_metadata_fields():
            if field.pattern:
                patterns[field.json_name] = field.pattern
            if field.readonly:
                blacklist.append(field.json_name)
            elif not field.optional:
                requires.append(field.json_name)
        result = {}
        if patterns:
            result['pattern'] = patterns
        if blacklist:
            result['blacklist'] = blacklist
        if requires:
            result['requires'] = requires
        result.update(rules)
        return result

    @classmethod
    def validate(cls, *args, **kwargs):
        validation_rules = cls.create_validation_rules(**kwargs)
        decorator = validate_form(**validation_rules)
        return decorator(args[0]) if args and callable(args[0]) else decorator

    @classmethod
    def expose(cls, func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = super(BaseModel, cls).expose(func)(*args, **kwargs)
            if result is None:
                raise HttpNotFound

            return result

        return wrapper

    @classmethod
    def to_form_params(cls):
        """ Get model parameters in ``webtest_docgen.FormParam`` """
        for c in cls.iter_dict_columns(relationships=False, include_readonly_columns=False, hybrids=False):
            column = cls.get_column(c)

            if hasattr(column, 'default') and column.default:
                default_ = column.default.arg if column.default.is_scalar else 'function(...)'
            else:
                default_ = ''

            try:
                type_ = column.type.python_type
            except NotImplementedError:
                type_ = str(column.type)

            yield FormParam(
                name=cls.get_dict_key(c),
                type_=type_,
                default=default_,
                required=not column.nullable,
                min_length=column.info.get('min_length'),
                max_length=column.info.get('max_length'),
                pattern=column.info.get('pattern'),
                example=column.info.get('example'),
            )


@event.listens_for(BaseModel, 'class_instrument')
def receive_class_instrument(cls):
    for field in cls.iter_columns(relationships=False, synonyms=False, use_inspection=False):
        if not isinstance(field, Field) or not field.can_validate:
            continue
        method_name = 'validate_%s' % field.name
        if not hasattr(cls, method_name):
            def validator(self, key, value):
                return self.get_column(key).validate(value)

            setattr(cls, method_name, validates(field.name)(validator))
