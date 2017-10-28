import copy
import unittest

from nanohttp import json, context

from microhttp_restful.validation import validate_form
from microhttp_restful.controllers import RestController, RootController
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import authorize


class ValidationExcludeController(RestController):

    @json
    @authorize
    @validate_form(exclude=['excludedParamForAll'],
                   client={'exclude': ['excludedParamForClient']},
                   admin={'exclude': ['excludedParamForAdmin']})
    def post(self):
        result = copy.deepcopy(context.form)
        result.update(context.query_string)
        return result


class Root(RootController):
    validation = ValidationExcludeController()


class ValidationExcludeTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()

    def test_validation_exclude(self):
        # Test `exclude`
        # role -> All
        resp = self.wsgi_app.post(
            '/validation',
            params={
                'customParam': 'param',
                'excludedParamForAll': 'param',
                'excludedParamForClient': 'param',
                'excludedParamForAdmin': 'param',
            }
        )
        self.assertIn('customParam', resp.text)
        self.assertIn('excludedParamForClient', resp.text)
        self.assertIn('excludedParamForAdmin', resp.text)
        self.assertNotIn('excludedParamForAll', resp.text)

        # -----------------------------
        # role -> Client
        self.wsgi_app.extra_environ['fake_roles'] = 'client'
        resp = self.wsgi_app.post(
            '/validation',
            params={
                'customParam': 'param',
                'excludedParamForAll': 'param',
                'excludedParamForClient': 'param',
                'excludedParamForAdmin': 'param',
            }
        )
        self.assertIn('customParam', resp.text)
        self.assertNotIn('excludedParamForClient', resp.text)
        self.assertIn('excludedParamForAdmin', resp.text)
        self.assertNotIn('excludedParamForAll', resp.text)

        # -----------------------------
        # role -> Admin
        self.wsgi_app.extra_environ['fake_roles'] = 'admin'
        resp = self.wsgi_app.post(
            '/validation',
            params={
                'customParam': 'param',
                'excludedParamForAll': 'param',
                'excludedParamForClient': 'param',
                'excludedParamForAdmin': 'param',
            }
        )
        self.assertIn('customParam', resp.text)
        self.assertIn('excludedParamForClient', resp.text)
        self.assertNotIn('excludedParamForAdmin', resp.text)
        self.assertNotIn('excludedParamForAll', resp.text)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
