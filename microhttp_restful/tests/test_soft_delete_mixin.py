import unittest

from sqlalchemy import Unicode

from nanohttp import HttpConflict

from microhttp.ext import db
from microhttp_restful import SoftDeleteMixin, Field
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import DeclarativeBase


class SoftDeleteCheckingModel(SoftDeleteMixin, DeclarativeBase):
    __tablename__ = 'soft_delete_checking_model'

    title = Field(Unicode(50), primary_key=True)


class SoftDeleteCheckingModelTestCase(WebAppTestCase):

    def test_soft_delete_mixin(self):
        db_session = db.get_session()

        # noinspection PyArgumentList
        instance = SoftDeleteCheckingModel(
            title='test title'
        )
        db_session.add(instance)
        db_session.commit()
        instance.assert_is_not_deleted()
        self.assertRaises(ValueError, instance.assert_is_deleted)

        instance = SoftDeleteCheckingModel.query.one()
        instance.soft_delete()
        db_session.commit()
        instance.assert_is_deleted()
        self.assertRaises(ValueError, instance.assert_is_not_deleted)

        self.assertEqual(SoftDeleteCheckingModel.filter_deleted().count(), 1)
        self.assertEqual(SoftDeleteCheckingModel.exclude_deleted().count(), 0)

        instance.soft_undelete()
        db_session.commit()
        instance.assert_is_not_deleted()
        self.assertRaises(ValueError, instance.assert_is_deleted)

        self.assertEqual(SoftDeleteCheckingModel.filter_deleted().count(), 0)
        self.assertEqual(SoftDeleteCheckingModel.exclude_deleted().count(), 1)

        db_session.delete(instance)
        self.assertRaises(HttpConflict, db_session.commit)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
