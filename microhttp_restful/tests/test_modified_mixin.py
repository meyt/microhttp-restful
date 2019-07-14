import unittest

from datetime import datetime
from freezegun import freeze_time

from sqlalchemy import Unicode

from microhttp.ext import db
from microhttp_restful import ModifiedMixin, Field
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import DeclarativeBase


class ModificationCheckingModel(ModifiedMixin, DeclarativeBase):
    __tablename__ = 'modification_checking_model'

    title = Field(Unicode(50), primary_key=True)


class ModificationCheckingModelTestCase(WebAppTestCase):

    def test_modified_mixin(self):
        expected_date = datetime.utcnow().replace(year=2001)
        with freeze_time(expected_date):
            db_session = db.get_session()
            # noinspection PyArgumentList
            instance = ModificationCheckingModel(
                title='test title',
            )

            db_session.add(instance)
            db_session.commit()
            self.assertIsNone(instance.modified_at)
            self.assertIsNotNone(instance.created_at)
            self.assertEqual(instance.last_modification_time, expected_date)
            self.assertEqual(instance.last_modification_time,
                             instance.created_at)

            instance = db_session.query(ModificationCheckingModel).one()
            self.assertIsNone(instance.modified_at)
            self.assertIsNotNone(instance.created_at)
            self.assertEqual(instance.last_modification_time, expected_date)
            self.assertEqual(instance.last_modification_time,
                             instance.created_at)

        expected_date = expected_date.replace(year=2002)
        with freeze_time(expected_date):
            instance.title = 'Edited title'
            db_session.commit()
            self.assertIsNotNone(instance.modified_at)
            self.assertIsNotNone(instance.created_at)
            self.assertEqual(instance.last_modification_time, expected_date)
            self.assertEqual(instance.last_modification_time,
                             instance.modified_at)

            instance = db_session.query(ModificationCheckingModel).one()
            self.assertIsNotNone(instance.modified_at)
            self.assertIsNotNone(instance.created_at)
            self.assertEqual(instance.last_modification_time, expected_date)
            self.assertEqual(instance.last_modification_time,
                             instance.modified_at)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
