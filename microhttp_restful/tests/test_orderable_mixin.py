import unittest

from sqlalchemy import Unicode

from microhttp.ext import db
from microhttp_restful import OrderableMixin, Field
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import DeclarativeBase


class OrderableCheckingModel(OrderableMixin, DeclarativeBase):
    __tablename__ = 'orderable_checking_model'

    title = Field(Unicode(50), primary_key=True)


class OrderableCheckingModelTestCase(WebAppTestCase):

    def test_orderable_mixin(self):
        db_session = db.get_session()
        for i in range(3):
            # noinspection PyArgumentList
            instance = OrderableCheckingModel(
                title='test title %s' % i,
                order=i
            )
            db_session.add(instance)
            db_session.commit()

        instances = OrderableCheckingModel.apply_default_sort().all()
        self.assertEqual(instances[0].order, 0)
        self.assertEqual(instances[2].order, 2)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
