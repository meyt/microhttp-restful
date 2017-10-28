import copy
import unittest

from nanohttp import json, context

from microhttp_restful.validation import validate_form
from microhttp_restful.controllers import RestController, RootController
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import authorize


class ValidationController(RestController):

    @json
    @authorize
    @validate_form(exact=['exactParamForAll'],
                   client={'exact': ['exactParamForClient']},
                   admin={'exact': ['exactParamForAdmin']})
    def post(self):
        result = copy.deepcopy(context.form)
        result.update(context.query_string)
        return result


class Root(RootController):
    validation = ValidationController()


class ValidationExactTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()

    def test_validation_exact(self):
        # Test `exact`
        # role -> All
        resp = self.wsgi_app.post('/validation', params={'exactParamForAll': 'param'})

        self.wsgi_app.post('/validation', status=400)
        self.wsgi_app.post('/validation', params={
            'exactParamForAll': 'param',
            'exactParamForCustom': 'param',
        }, status=400)

        self.wsgi_app.post('/validation', params={'exactParamForCustom': 'param'}, status=400)

        self.assertIn('exactParamForAll', resp.text)
        self.wsgi_app.post('/validation', params={
            'exactParamForAll': 'param',
            'exactParamForClient': 'param',
        }, status=400)

        # -----------------------------
        # role -> Client
        self.wsgi_app.extra_environ['fake_roles'] = 'client'

        resp = self.wsgi_app.post(
            '/validation',
            params={
                'exactParamForAll': 'param',
                'exactParamForClient': 'param',
            }
        )
        self.assertIn('exactParamForClient', resp.text)
        self.assertIn('exactParamForAll', resp.text)

        self.wsgi_app.post(
            '/validation',
            params={
                'exactParamForAll': 'param',
                'exactParamForClient': 'param',
                'exactParamForAdmin': 'param',
            },
            status=400
        )

        # -----------------------------
        # role -> Admin
        self.wsgi_app.extra_environ['fake_roles'] = 'admin'

        resp = self.wsgi_app.post(
            '/validation',
            params={
                'exactParamForAll': 'param',
                'exactParamForAdmin': 'param',
            }
        )
        self.assertIn('exactParamForAdmin', resp.text)
        self.assertIn('exactParamForAll', resp.text)

        self.wsgi_app.post(
            '/validation',
            params={
                'exactParamForAll': 'param',
                'exactParamForClient': 'param',
                'exactParamForAdmin': 'param',
            },
            status=400
        )

        # ------------------------------------------------------------

        # Test query string
        self.wsgi_app.extra_environ['fake_roles'] = 'admin'
        resp = self.wsgi_app.post(
            '/validation?exactParamForAll=param',
            params={
                'exactParamForAdmin': 'param',
            }
        )
        self.assertIn('exactParamForAdmin', resp.text)
        self.assertIn('exactParamForAll', resp.text)

        self.wsgi_app.post(
            '/validation?exactParamForAll=param&exactParamForClient=param',
            params={
                'exactParamForAdmin': 'param',
            },
            status=400
        )

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
