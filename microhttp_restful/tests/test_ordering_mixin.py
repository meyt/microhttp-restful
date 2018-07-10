import unittest

from sqlalchemy import Integer, Unicode, Boolean
from sqlalchemy.orm import synonym

from nanohttp.contexts import Context

from microhttp.ext import db
from microhttp_restful import OrderingMixin, Field
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import DeclarativeBase


class OrderingObject(OrderingMixin, DeclarativeBase):
    __tablename__ = 'ordering_object'

    id = Field(Integer, primary_key=True)
    title = Field(Unicode(50), collation='persian')
    is_active = Field(Boolean, nullable=True)
    _age = Field(Integer)

    def _set_age(self, age):
        self._age = age

    def _get_age(self):  # pragma: no cover
        return self._age

    age = synonym('_age', descriptor=property(_get_age, _set_age))


class OrderingMixinTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.session.execute('CREATE COLLATION persian (LOCALE = \'fa_IR.utf8\');')

    # noinspection PyArgumentList
    def test_ordering_mixin(self):
        db_session = db.get_session()
        db_session.add(OrderingObject(title='Title is active', is_active=True, age=1))
        db_session.add(OrderingObject(title='Title is not active', is_active=False, age=2))
        db_session.add(OrderingObject(title='آیینه', is_active=False, age=3))
        db_session.add(OrderingObject(title='آرامش', is_active=False, age=4))

        for i in range(1, 6):
            obj = OrderingObject(title='object %s' % i, age=i * 10)
            db_session.add(obj)
        db_session.commit()

        # Default soring
        with Context({'QUERY_STRING': ''}, self.application):
            result = OrderingObject.sort_by_request().all()
            self.assertEqual(len(result), 9)

        # Ascending
        with Context({'QUERY_STRING': 'sort=id'}, self.application):
            result = OrderingObject.sort_by_request().all()
            self.assertEqual(result[0].id, 1)
            self.assertEqual(result[-1].id, 9)

        # Descending
        with Context({'QUERY_STRING': 'sort=-id'}, self.application):
            result = OrderingObject.sort_by_request().all()
            self.assertEqual(result[0].id, 9)
            self.assertEqual(result[-1].id, 1)

        # Sort by Synonym Property
        with Context({'QUERY_STRING': 'sort=age'}, self.application):
            result = OrderingObject.sort_by_request().all()
            self.assertEqual(result[0].id, 1)
            self.assertEqual(result[-1].id, 9)

        # Sort for collation specified field
        with Context({'QUERY_STRING': 'sort=title'}, self.application):
            result = OrderingObject.sort_by_request().all()
            self.assertEqual(result[7].title, 'آرامش')
            self.assertEqual(result[8].title, 'آیینه')
            self.assertEqual(result[0].id, 5)
            self.assertEqual(result[-1].id, 3)

        # TODO add test for sorting with multiple columns and check the order of columns


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
