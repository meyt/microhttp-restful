import re
import copy
import unittest

from nanohttp import json, context

from microhttp_restful.validation import validate_form
from microhttp_restful.controllers import RestController, RootController
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import authorize


class ValidationPatternController(RestController):

    @json
    @authorize
    @validate_form(
        pattern={
            'patternedParam1': re.compile(r'^\d{10}$'),
            'patternedParam2': '^\D{10}$',
            'patternedParam3': re.compile(r'^Exact$'),
        },
        client={
           'pattern': {
               'patternedParam1': re.compile(r'^\d{5}$'),
               'patternedParam2': re.compile(r'^\D{5}$')
           }
        },
        admin={
           'pattern': {
               'patternedParam1': '^\d+$',
               'patternedParam4': re.compile(r'^SuperAdmin$')
           }
        }
    )
    def post(self):
        result = copy.deepcopy(context.form)
        result.update(context.query_string)
        return result


class Root(RootController):
    validation = ValidationPatternController()


class ValidationPatternTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()

    def test_validation_pattern(self):
        # Test `exclude`
        # role -> All
        self.wsgi_app.post(
            '/validation',
            params={
                'patternedParam1': '0123456789',
                'patternedParam2': 'abcdeFGHIJ',
                'patternedParam3': 'Exact'
            }
        )

        self.wsgi_app.post(
            '/validation',
            params={'patternedParam1': '12345'},
            status=400
        )

        # -----------------------------
        # role -> Client
        self.wsgi_app.extra_environ['fake_roles'] = 'client'
        self.wsgi_app.post(
            '/validation',
            params={
                'patternedParam1': '12345',
                'patternedParam2': 'ABCDE',
                'patternedParam3': 'Exact',
                'patternedParam4': 'anything'
            }
        )

        self.wsgi_app.post(
            '/validation',
            params={'patternedParam1': '1'},
            status=400
        )

        # -----------------------------
        # role -> Admin
        self.wsgi_app.extra_environ['fake_roles'] = 'admin'
        self.wsgi_app.post(
            '/validation',
            params={
                'patternedParam1': '1',
                'patternedParam2': 'ABCDEFGHIJ',
                'patternedParam4': 'SuperAdmin'
            }
        )
        self.wsgi_app.post(
            '/validation',
            params={'patternedParam4': 'anything'},
            status=400
        )


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
