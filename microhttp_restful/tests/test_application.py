import unittest

from nanohttp import action

from microhttp_restful.controllers import RootController
from microhttp_restful.tests.helpers import WebAppTestCase


class Root(RootController):

    @action
    def index(self):
        return 'Index'


class ApplicationTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()

    def test_index(self):
        resp = self.wsgi_app.get('/')
        self.assertEqual(resp.body, b'Index')

    def test_options(self):
        resp = self.wsgi_app.options('/')
        self.assertEqual(resp.headers['Cache-Control'], 'no-cache,no-store')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
