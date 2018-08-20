import unittest

from sqlalchemy import Integer, Unicode, Boolean

from nanohttp import json

from microhttp.ext import db
from microhttp_restful import Field, DefaultsMixin
from microhttp_restful.controllers import RestController, RootController
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import DeclarativeBase


class Store(DefaultsMixin, DeclarativeBase):
    __tablename__ = 'store'
    __default_fields__ = ('default_for_apple', 'default_for_orange')
    id = Field(Integer, primary_key=True)
    title = Field(Unicode(50))
    default_for_apple = Field(Boolean, nullable=True, unique=True)
    default_for_orange = Field(Boolean, nullable=True, unique=True)


class StoreController(RestController):

    @json
    @db.commit
    def put(self, store_id: int=None):
        db_session = db.get_session()
        if len(list(Store.reset_defaults_from_request())) > 0:
            db_session.begin_nested()

        store = Store.query.get(store_id)
        store.update_from_request()
        return store


class Root(RootController):
    store = StoreController()


class DefaultsMixinTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()

    # noinspection PyArgumentList
    def test_defaults_mixin(self):
        db_session = db.get_session()
        harry_store = Store(title='Harry Store')
        sarah_store = Store(title='Sarah Store')
        john_store = Store(title='John Store')
        db_session.add(harry_store)
        db_session.add(sarah_store)
        db_session.add(john_store)
        db_session.commit()

        self.wsgi_app.put(
            '/store/%s' % sarah_store.id,
            params={
                'defaultForApple': True
            }
        )

        john_store = Store.query.get(john_store.id)
        self.assertEqual(john_store.default_for_apple, None)

        harry_store = Store.query.get(harry_store.id)
        self.assertEqual(harry_store.default_for_apple, None)

        sarah_store = Store.query.get(sarah_store.id)
        self.assertEqual(sarah_store.default_for_apple, True)

        # Change default
        self.wsgi_app.put(
            '/store/%s' % john_store.id,
            params={
                'defaultForApple': True
            }
        )

        john_store = Store.query.get(john_store.id)
        self.assertEqual(john_store.default_for_apple, True)

        harry_store = Store.query.get(harry_store.id)
        self.assertEqual(harry_store.default_for_apple, None)

        sarah_store = Store.query.get(sarah_store.id)
        self.assertEqual(sarah_store.default_for_apple, None)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
