import copy
import unittest

from nanohttp import json, context

from microhttp_restful.validation import validate_form
from microhttp_restful.controllers import RestController, RootController
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import authorize


class ValidationFilterController(RestController):

    @json
    @authorize
    @validate_form(
        filter_=['filteredParamForAll'],
        client=dict(filter_=['filteredParamForClient']),
        admin=dict(filter_=['filteredParamForAdmin'])
    )
    def post(self):
        result = copy.deepcopy(context.form)
        result.update(context.query_string)
        return result


class Root(RootController):
    validation = ValidationFilterController()


class ValidationFilterTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()

    def test_validation_filter(self):
        # Test `filter`
        # role -> All
        resp = self.wsgi_app.post(
            '/validation',
            params={
                'customParam': 'param',
                'filteredParamForAll': 'param',
                'filteredParamForClient': 'param',
                'filteredParamForAdmin': 'param',
            }
        )
        self.assertNotIn('customParam', resp.text)
        self.assertNotIn('filteredParamForClient', resp.text)
        self.assertNotIn('filteredParamForAdmin', resp.text)
        self.assertIn('filteredParamForAll', resp.text)

        # -----------------------------
        # role -> Client
        self.wsgi_app.extra_environ['fake_roles'] = 'client'
        resp = self.wsgi_app.post(
            '/validation',
            params={
                'customParam': 'param',
                'filteredParamForAll': 'param',
                'filteredParamForClient': 'param',
                'filteredParamForAdmin': 'param',
            }
        )
        self.assertNotIn('customParam', resp.text)
        self.assertIn('filteredParamForClient', resp.text)
        self.assertNotIn('filteredParamForAdmin', resp.text)
        self.assertIn('filteredParamForAll', resp.text)

        # -----------------------------
        # role -> Admin
        self.wsgi_app.extra_environ['fake_roles'] = 'admin'
        resp = self.wsgi_app.post(
            '/validation',
            params={
                'customParam': 'param',
                'filteredParamForAll': 'param',
                'filteredParamForClient': 'param',
                'filteredParamForAdmin': 'param',
            }
        )
        self.assertNotIn('customParam', resp.text)
        self.assertNotIn('filteredParamForClient', resp.text)
        self.assertIn('filteredParamForAdmin', resp.text)
        self.assertIn('filteredParamForAll', resp.text)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
