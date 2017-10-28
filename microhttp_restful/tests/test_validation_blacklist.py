import copy
import unittest

from nanohttp import json, context

from microhttp_restful.validation import validate_form
from microhttp_restful.controllers import RestController, RootController
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import authorize


class ValidationBlackListController(RestController):
    @json
    @authorize
    @validate_form(blacklist=['blacklistParamForAll'],
                   client={'blacklist': ['blacklistParamForClient']},
                   admin={'blacklist': ['blacklistParamForAdmin']})
    def post(self):
        result = copy.deepcopy(context.form)
        result.update(context.query_string)
        return result


class Root(RootController):
    validation = ValidationBlackListController()


class ValidationBlackListTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()

    def test_x(self):
        # Test `blacklist`
        # role -> All
        self.wsgi_app.post('/validation', params={'customParam': 'param'})
        self.wsgi_app.post('/validation')
        self.wsgi_app.post('/validation', params={'customParam': 'param'})
        self.wsgi_app.post('/validation', params={'blacklistParamForAll': 'param'}, status=400)
        self.wsgi_app.post('/validation', params={'blacklistParamForClient': 'param'})
        self.wsgi_app.post('/validation', params={'blacklistParamForAdmin': 'param'})

        # -----------------------------
        # role -> Client
        self.wsgi_app.extra_environ['fake_roles'] = 'client'
        self.wsgi_app.post('/validation')
        self.wsgi_app.post('/validation', params={'customParam': 'param'})
        self.wsgi_app.post('/validation', params={'blacklistParamForAll': 'param'}, status=400)
        self.wsgi_app.post('/validation', params={'blacklistParamForClient': 'param'}, status=400)
        self.wsgi_app.post('/validation', params={'blacklistParamForAdmin': 'param'})

        # -----------------------------
        # role -> Admin
        self.wsgi_app.extra_environ['fake_roles'] = 'admin'
        self.wsgi_app.post('/validation')
        self.wsgi_app.post('/validation', params={'customParam': 'param'})
        self.wsgi_app.post('/validation', params={'blacklistParamForAll': 'param'}, status=400)
        self.wsgi_app.post('/validation', params={'blacklistParamForClient': 'param'})
        self.wsgi_app.post('/validation', params={'blacklistParamForAdmin': 'param'}, status=400)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
