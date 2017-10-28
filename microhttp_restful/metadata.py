

class MetadataField(object):
    def __init__(self, json_name, key, type_=str, default_=None, optional=None,
                 pattern=None, max_length=None, min_length=None, message='Invalid value',
                 watermark=None, label=None, icon=None, example=None, primary_key=False, readonly=False,
                 protected=False):
        self.json_name = json_name
        self.key = key[1:] if key.startswith('_') else key
        self.type_ = type_
        self.default_ = default_
        self.optional = optional
        self.pattern = pattern
        self.max_length = max_length
        self.min_length = min_length
        self.message = message
        self.watermark = watermark
        self.label = label or watermark
        self.icon = icon
        self.example = example
        self.primary_key = primary_key
        self.readonly = readonly
        self.protected = protected

    @property
    def type_name(self):
        return self.type_ if isinstance(self.type_, str) else self.type_.__name__

    def to_json(self):
        return dict(
            name=self.json_name,
            key=self.key,
            type_=self.type_name,
            default=self.default_,
            optional=self.optional,
            pattern=self.pattern,
            maxLength=self.max_length,
            minLength=self.min_length,
            message=self.message,
            watermark=self.watermark,
            label=self.label,
            icon=self.icon,
            example=self.example,
            primaryKey=self.primary_key,
            readonly=self.readonly,
            protected=self.protected
        )

    @classmethod
    def from_column(cls, c, json_name, info=None):
        if not info:
            info = c.info
        result = []

        key = c.key

        if hasattr(c, 'default') and c.default:
            default_ = c.default.arg if c.default.is_scalar else None
        else:
            default_ = None

        if hasattr(c, 'type'):
            try:
                type_ = c.type.python_type
            except NotImplementedError:
                # As we spoke, hybrid properties have no type
                type_ = ''
        # Commented out because cannot reach here by tests
        # elif hasattr(c, 'target'):
        #     try:
        #         type_ = c.target.name
        #     except AttributeError:  # pragma: no cover
        #         type_ = c.target.right.name
        else:  # pragma: no cover
            type_ = 'str'
            # raise AttributeError('Unable to recognize type of the column: %s' % c.key)

        result.append(cls(
            json_name,
            key,
            type_=type_,
            default_=default_,
            optional=c.nullable if hasattr(c, 'nullable') else None,
            pattern=info.get('pattern'),
            max_length=info.get('max_length',
                                (c.type.length if hasattr(c, 'type') and hasattr(c.type, 'length') else None)),
            min_length=info.get('min_length'),
            message=info.get('message', 'Invalid Value'),
            watermark=info.get('watermark', None),
            label=info.get('label', None),
            icon=info.get('icon', None),
            example=info.get('example', None),
            primary_key=hasattr(c.expression, 'primary_key') and c.expression.primary_key,
            readonly=info.get('readonly', False),
            protected=info.get('protected', False)
        ))

        return result
