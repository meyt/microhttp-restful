import re
from sqlalchemy import Unicode, String
from sqlalchemy_dict import Field as SADictField
from nanohttp import HttpBadRequest


# noinspection PyAbstractClass
class Field(SADictField):

    def __init__(self,
                 *args,
                 max_length=None,
                 min_length=None,
                 pattern=None,
                 watermark=None,
                 nullable=False,
                 label=None,
                 icon=None,
                 example=None,
                 message=None,
                 info=None,
                 **kwargs):
        info = info or dict()

        if watermark is not None:
            info['watermark'] = watermark

        if max_length is not None:
            info['max_length'] = max_length
        elif args and isinstance(args[0], (Unicode, String)):
            info['max_length'] = args[0].length

        if min_length is not None:
            info['min_length'] = min_length

        if pattern is not None:
            info['pattern'] = pattern

        if label is not None:
            info['label'] = label

        if icon is not None:
            info['icon'] = icon

        if example is not None:
            info['example'] = example

        if message is not None:
            info['message'] = message

        super(Field, self).__init__(*args, info=info, nullable=nullable, **kwargs)

    @property
    def can_validate(self):
        return 'pattern' in self.info or \
            'min_length' in self.info or \
            'max_length' in self.info

    def _validate_pattern(self, value):
        if value is None:
            return
        if not re.match(self.info['pattern'], value):
            raise HttpBadRequest('Cannot match field: %s with value "%s" by acceptable pattern' % (self.name, value))
        return value

    def _validate_length(self, value, min_length, max_length):
        if value is None:
            return

        if not isinstance(value, str):
            raise HttpBadRequest('Invalid type: %s for field: %s' % (type(value), self.name))

        value_length = len(value)
        if min_length is not None:
            if value_length < min_length:
                raise HttpBadRequest('Please enter at least %d characters for field: %s.' % (min_length, self.name))

        if max_length is not None:
            if value_length > max_length:
                raise HttpBadRequest('Cannot enter more than: %d in field: %s.' % (max_length, self.name))

    def validate(self, value):
        if 'pattern' in self.info:
            self._validate_pattern(value)

        if 'min_length' in self.info or 'max_length' in self.info:
            self._validate_length(value, self.info.get('min_length'), self.info.get('max_length'))
        return value
