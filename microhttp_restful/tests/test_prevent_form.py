import unittest

from nanohttp import json

from microhttp_restful.validation import prevent_form
from microhttp_restful.controllers import RestController, RootController
from microhttp_restful.tests.helpers import WebAppTestCase


class ValidationPreventFormController(RestController):
    @json
    @prevent_form
    def post(self):
        return dict()


class Root(RootController):
    validation = ValidationPreventFormController()


class ValidationPreventFormTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()

    def test_validation_prevent_form(self):
        # Good
        self.wsgi_app.post(
            '/validation'
        )

        # Bad
        self.wsgi_app.post(
            '/validation',
            params={'param': 'param'},
            status=400
        )
        self.wsgi_app.post(
            '/validation?param=param',
            status=400
        )

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
