import copy
import unittest

from nanohttp import json, context

from microhttp_restful.validation import validate_form
from microhttp_restful.controllers import RestController, RootController
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import authorize


class ValidationRequiresController(RestController):

    @json
    @authorize
    @validate_form(requires=['requiresParamForAll'],
                   client={'requires': ['requiresParamForClient']},
                   admin={'requires': ['requiresParamForAdmin']})
    def post(self):
        result = copy.deepcopy(context.form)
        result.update(context.query_string)
        return result


class Root(RootController):
    validation = ValidationRequiresController()


class ValidationRequiresTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()

    def test_validation_requires(self):
        # Test `requires`
        # role -> All
        resp = self.wsgi_app.post(
            '/validation',
            params={'requiresParamForAll': 'param'}
        )
        self.assertIn('requiresParamForAll', resp.json)

        resp = self.wsgi_app.post(
            '/validation',
            params={
                'customParam': 'param',
                'requiresParamForAll': 'param',
            }
        )
        self.assertIn('customParam', resp.json)
        self.assertIn('requiresParamForAll', resp.json)

        self.wsgi_app.post(
            '/validation',
            status=400
        )

        self.wsgi_app.post(
            '/validation',
            params={'customParam': 'param'},
            status=400
        )

        self.wsgi_app.post(
            '/validation',
            params={'requiresParamForClient': 'param'},
            status=400
        )

        # -----------------------------
        # role -> Client
        self.wsgi_app.extra_environ['fake_roles'] = 'client'
        resp = self.wsgi_app.post(
            '/validation',
            params={
                'requiresParamForAll': 'param',
                'requiresParamForClient': 'param',
            }
        )
        self.assertIn('requiresParamForAll', resp.json)
        self.assertIn('requiresParamForClient', resp.json)

        resp = self.wsgi_app.post(
            '/validation',
            params={
                'customParam': 'param',
                'requiresParamForAll': 'param',
                'requiresParamForClient': 'param',
            }
        )
        self.assertIn('customParam', resp.json)
        self.assertIn('requiresParamForAll', resp.json)
        self.assertIn('requiresParamForClient', resp.json)

        self.wsgi_app.post(
            '/validation',
            status=400
        )

        self.wsgi_app.post(
            '/validation',
            params={'customParam': 'param'},
            status=400
        )

        self.wsgi_app.post(
            '/validation',
            params={'requiresParamForAll': 'param'},
            status=400
        )

        self.wsgi_app.post(
            '/validation',
            params={'requiresParamForClient': 'param'},
            status=400
        )

        # -----------------------------
        # role -> Admin
        self.wsgi_app.extra_environ['fake_roles'] = 'admin'
        resp = self.wsgi_app.post(
            '/validation',
            params={
                'requiresParamForAll': 'param',
                'requiresParamForAdmin': 'param',
            }
        )
        self.assertIn('requiresParamForAll', resp.json)
        self.assertIn('requiresParamForAdmin', resp.json)

        resp = self.wsgi_app.post(
            '/validation',
            params={
                'customParam': 'param',
                'requiresParamForAll': 'param',
                'requiresParamForAdmin': 'param',
            }
        )
        self.assertIn('customParam', resp.json)
        self.assertIn('requiresParamForAll', resp.json)
        self.assertIn('requiresParamForAdmin', resp.json)

        self.wsgi_app.post(
            '/validation',
            status=400
        )

        self.wsgi_app.post(
            '/validation',
            params={'customParam': 'param'},
            status=400
        )

        self.wsgi_app.post(
            '/validation',
            params={
                'requiresParamForAll': 'param',
                'requiresParamForClient': 'param',
            },
            status=400
        )

        self.wsgi_app.post(
            '/validation',
            params={'requiresParamForAdmin': 'param'},
            status=400
        )


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
