from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.events import event

from nanohttp import HttpConflict

from microhttp_restful import Field


class SoftDeleteMixin:
    removed_at = Field(DateTime, nullable=True, readonly=True)

    def assert_is_not_deleted(self):
        if self.is_deleted:
            raise ValueError('Object is already deleted.')

    def assert_is_deleted(self):
        if not self.is_deleted:
            raise ValueError('Object is not deleted.')

    @property
    def is_deleted(self):
        return self.removed_at is not None

    def soft_delete(self, ignore_errors=False):
        if not ignore_errors:
            self.assert_is_not_deleted()
        self.removed_at = datetime.now()

    def soft_undelete(self, ignore_errors=False):
        if not ignore_errors:
            self.assert_is_deleted()
        self.removed_at = None

    @staticmethod
    def before_delete(mapper, connection, target):
        raise HttpConflict('Cannot remove this object: %s' % target)

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, 'before_delete', cls.before_delete)

    @classmethod
    def filter_deleted(cls, query=None):
        # noinspection PyUnresolvedReferences
        return (query or cls.query).filter(cls.removed_at.isnot(None))

    @classmethod
    def exclude_deleted(cls, query=None):
        # noinspection PyUnresolvedReferences
        return (query or cls.query).filter(cls.removed_at.is_(None))
