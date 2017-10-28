import unittest

from sqlalchemy import Unicode

from nanohttp import json, etag, context

from microhttp.ext import db

from microhttp_restful.controllers import ModelRestController
from microhttp_restful import ModifiedMixin, Field
from microhttp_restful.tests.helpers import WebAppTestCase, DeclarativeBase


class EtagCheckingModel(ModifiedMixin, DeclarativeBase):
    __tablename__ = 'etag_checking_model'

    title = Field(Unicode(50), primary_key=True)

    @property
    def __etag__(self):
        return self.last_modification_time.isoformat()


class Root(ModelRestController):
    __model__ = EtagCheckingModel

    @json
    @etag
    @db.commit
    def post(self):
        db_session = db.get_session()
        m = EtagCheckingModel()
        m.update_from_request()
        db_session.add(m)
        return m

    @json
    @EtagCheckingModel.expose
    @etag
    def get(self, title: str):
        query = EtagCheckingModel.query
        return query.filter(EtagCheckingModel.title == title).one_or_none()

    @json
    @EtagCheckingModel.expose
    @etag
    @db.commit
    def put(self, title: str=None):
        db_session = db.get_session()
        m = db_session.query(EtagCheckingModel).filter(EtagCheckingModel.title == title).one_or_none()
        m.update_from_request()
        context.etag_match(m.__etag__)
        return m


class EtagCheckingModelTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()

    def test_etag_match(self):
        resp = self.wsgi_app.post(
            '/',
            params={
                'title': 'etag_test'
            }
        )
        self.assertIn('ETag', resp.headers)
        initial_etag = resp.headers['ETag']

        # Getting the resource with known etag, expected 304
        self.wsgi_app.get(
            '/etag_test',
            headers={
                'If-None-Match': initial_etag
            },
            status=304
        )

        # Putting without the etag header, expected error: Precondition Failed
        self.wsgi_app.put(
            '/etag_test',
            params={
                'title': 'etag_test_edit1'
            },
            status=412
        )

        # Putting with the etag header, expected: success
        resp = self.wsgi_app.put(
            '/etag_test',
            params={
                'title': 'etag_test_edit1'
            },
            headers={
                'If-Match': initial_etag
            }
        )
        self.assertIn('ETag', resp.headers)
        etag_after_put = resp.headers['ETag']
        self.assertNotEqual(initial_etag, etag_after_put)

        # Getting the resource with known etag, expected 304
        self.wsgi_app.get(
            '/etag_test_edit1',
            headers={
                'If-None-Match': initial_etag
            },
            status=200
        )
        self.assertIn('ETag', resp.headers)
        new_etag = resp.headers['ETag']
        self.assertNotEqual(new_etag, initial_etag)
        self.assertEqual(new_etag, etag_after_put)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
