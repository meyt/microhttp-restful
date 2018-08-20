from typing import Union, Generator

from nanohttp import context

from sqlalchemy_dict.utils import to_camel_case


class DefaultsMixin:
    __default_fields__ = ()

    @classmethod
    def find_fields_to_reset(cls, values: dict) -> Generator:
        """
        Find default fields have True value and need reset
        (before update_from_request).
        :param values:
        :return:
        """
        for field_name in cls.__default_fields__:
            field_dict_name = to_camel_case(field_name)
            field_value = values.get(field_dict_name)

            if (
                isinstance(field_value, bool) and field_value is True
            ) or (
                isinstance(field_value, str) and field_value.lower() == 'true'
            ):
                yield field_name

    # noinspection PyUnresolvedReferences
    @classmethod
    def reset_defaults(cls, fields: Union[tuple, list, Generator]) -> Generator:
        """
        Set null value for default fields
        :param fields
        :return: Changed fields
        """
        for field_name in fields:
            item = cls.query.filter(
                getattr(cls, field_name).is_(True)
            ).first()
            if item:
                setattr(item, field_name, None)
                yield field_name

    @classmethod
    def reset_defaults_from_request(cls) -> Generator:
        """
        Reset default fields by values exist in request context.
        :return:
        """
        return cls.reset_defaults(
            cls.find_fields_to_reset(context.form)
        )
