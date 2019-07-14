import unittest

from datetime import datetime
from freezegun import freeze_time

from sqlalchemy import Unicode

from microhttp.ext import db
from microhttp_restful import CreatedMixin, Field
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import DeclarativeBase


class Message(CreatedMixin, DeclarativeBase):
    __tablename__ = 'message'

    content = Field(Unicode(50), primary_key=True)


class CreatedCheckingModelTestCase(WebAppTestCase):

    def test_created_mixin(self):
        expected_date = datetime.utcnow().replace(year=2001)
        with freeze_time(expected_date):
            db_session = db.get_session()
            # noinspection PyArgumentList
            instance = Message(
                content='test content',
            )

            db_session.add(instance)
            db_session.commit()
            self.assertIsNotNone(instance.created_at)
            self.assertEqual(expected_date, instance.created_at)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
