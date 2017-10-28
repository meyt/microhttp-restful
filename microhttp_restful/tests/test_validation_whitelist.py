import copy
import unittest

from nanohttp import json, context

from microhttp_restful.validation import validate_form
from microhttp_restful.controllers import RestController, RootController
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import authorize


class ValidationWhitelistController(RestController):

    @json
    @authorize
    @validate_form(whitelist=['whitelistParamForAll'],
                   client={'whitelist': ['whitelistParamForClient']},
                   admin={'whitelist': ['whitelistParamForAdmin']})
    def post(self):
        result = copy.deepcopy(context.form)
        result.update(context.query_string)
        return result


class Root(RootController):
    validation = ValidationWhitelistController()


class ValidationWhitelistTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()

    def test_validation_whitelist(self):
        # Test `whitelist`
        # role -> All
        resp = self.wsgi_app.post(
            '/validation',
            params={'whitelistParamForAll': 'param'}
        )
        self.assertIn('whitelistParamForAll', resp.json)
        self.wsgi_app.post(
            '/validation'
        )
        self.wsgi_app.post(
            '/validation',
            params={
                'whitelistParamForAll': 'param',
                'customParam': 'param'
            },
            status=400
        )
        self.wsgi_app.post(
            '/validation',
            params={'customParam': 'param'},
            status=400
        )
        self.wsgi_app.post(
            '/validation',
            params={'whitelistParamForClient': 'param'},
            status=400
        )

        # -----------------------------
        # role -> Client
        self.wsgi_app.extra_environ['fake_roles'] = 'client'
        resp = self.wsgi_app.post(
            '/validation',
            params={'whitelistParamForAll': 'param'}
        )
        self.assertIn('whitelistParamForAll', resp.json)

        resp = self.wsgi_app.post(
            '/validation',
            params={'whitelistParamForClient': 'param'}
        )
        self.assertIn('whitelistParamForClient', resp.json)

        resp = self.wsgi_app.post(
            '/validation',
            params={
                'whitelistParamForAll': 'param',
                'whitelistParamForClient': 'param',
            }
        )
        self.assertIn('whitelistParamForAll', resp.json)
        self.assertIn('whitelistParamForClient', resp.json)

        self.wsgi_app.post(
            '/validation'
        )

        self.wsgi_app.post(
            '/validation',
            params={
                'whitelistParamForAll': 'param',
                'customParam': 'param',
            },
            status=400
        )

        self.wsgi_app.post(
            '/validation',
            params={
                'customParam': 'param',
            },
            status=400
        )

        self.wsgi_app.post(
            '/validation',
            params={
                'whitelistParamForAdmin': 'param',
            },
            status=400
        )

        # -----------------------------
        # role -> Admin
        self.wsgi_app.extra_environ['fake_roles'] = 'admin'
        resp = self.wsgi_app.post(
            '/validation',
            params={'whitelistParamForAll': 'param'}
        )
        self.assertIn('whitelistParamForAll', resp.json)

        resp = self.wsgi_app.post(
            '/validation',
            params={'whitelistParamForAdmin': 'param'}
        )
        self.assertIn('whitelistParamForAdmin', resp.json)

        resp = self.wsgi_app.post(
            '/validation',
            params={
                'whitelistParamForAll': 'param',
                'whitelistParamForAdmin': 'param',
            }
        )
        self.assertIn('whitelistParamForAll', resp.json)
        self.assertIn('whitelistParamForAdmin', resp.json)

        self.wsgi_app.post(
            '/validation'
        )

        self.wsgi_app.post(
            '/validation',
            params={
                'whitelistParamForAll': 'param',
                'customParam': 'param',
            },
            status=400
        )

        self.wsgi_app.post(
            '/validation',
            params={
                'customParam': 'param',
            },
            status=400
        )

        self.wsgi_app.post(
            '/validation',
            params={
                'whitelistParamForAll': 'param',
                'whitelistParamForAdmin': 'param',
                'whitelistParamForClient': 'param',
            },
            status=400
        )


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
