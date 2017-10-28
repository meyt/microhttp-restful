from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.events import event

from microhttp_restful import Field
from microhttp_restful.mixins.created import CreatedMixin


class ModifiedMixin(CreatedMixin):
    modified_at = Field(DateTime, nullable=True, readonly=True)

    @property
    def last_modification_time(self):
        return self.modified_at or self.created_at

    # noinspection PyUnusedLocal
    @staticmethod
    def before_update(mapper, connection, target):
        target.modified_at = datetime.now()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, 'before_update', cls.before_update)
