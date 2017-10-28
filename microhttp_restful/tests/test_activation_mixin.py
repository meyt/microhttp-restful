import unittest

from sqlalchemy import Integer, Unicode

from microhttp.ext import db
from microhttp_restful import ActivationMixin, Field
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import DeclarativeBase


class ActiveObject(ActivationMixin, DeclarativeBase):
    __tablename__ = 'active_object'

    id = Field(Integer, primary_key=True)
    title = Field(Unicode(50))


class ActivationMixinTestCase(WebAppTestCase):

    def test_activation_mixin(self):
        db_session = db.get_session()
        # noinspection PyArgumentList
        object1 = ActiveObject(
            title='object 1',
        )

        db_session.add(object1)
        db_session.commit()

        self.assertFalse(object1.is_active)
        self.assertEqual(db_session.query(ActiveObject).filter(ActiveObject.is_active).count(), 0)

        object1.is_active = True
        self.assertTrue(object1.is_active)
        db_session.commit()
        object1 = db_session.query(ActiveObject).one()
        self.assertTrue(object1.is_active)

        json = object1.to_dict()
        self.assertIn('isActive', json)

        self.assertEqual(db_session.query(ActiveObject).filter(ActiveObject.is_active).count(), 1)
        self.assertEqual(ActiveObject.filter_activated().count(), 1)

        self.assertFalse(ActiveObject.import_value(ActiveObject.is_active, 'false'))
        self.assertFalse(ActiveObject.import_value(ActiveObject.is_active, 'FALSE'))
        self.assertFalse(ActiveObject.import_value(ActiveObject.is_active, 'False'))
        self.assertTrue(ActiveObject.import_value(ActiveObject.is_active, 'true'))
        self.assertTrue(ActiveObject.import_value(ActiveObject.is_active, 'TRUE'))
        self.assertTrue(ActiveObject.import_value(ActiveObject.is_active, 'True'))

        self.assertEqual(ActiveObject.import_value(ActiveObject.title, 'title'), 'title')

    def test_metadata(self):
        # Metadata
        object_metadata = ActiveObject.json_metadata()
        self.assertIn('id', object_metadata['fields'])
        self.assertIn('title', object_metadata['fields'])
        self.assertIn('isActive', object_metadata['fields'])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
