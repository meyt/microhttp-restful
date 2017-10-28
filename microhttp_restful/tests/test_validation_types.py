import copy
import unittest

from nanohttp import json, context

from microhttp_restful.validation import validate_form
from microhttp_restful.controllers import RestController, RootController
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import authorize


class ValidationTypesController(RestController):

    @json
    @authorize
    @validate_form(
        types={
            'typedParam1': float,
            'typedParam2': float,
            'typedParam3': float,
        },
        client={
           'types': {
               'typedParam1': int,
               'typedParam2': int
           }
        },
        admin={
           'types': {
               'typedParam1': complex,
               'typedParam4': complex
           }
        }
    )
    def post(self):
        result = copy.deepcopy(context.form)
        result.update(context.query_string)
        return result


class Root(RootController):
    validation = ValidationTypesController()


class ValidationTypesTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()

    def test_validation_types(self):
        # Test `type`
        # role -> All
        resp = self.wsgi_app.post(
            '/validation',
            params={
                'typedParam1': '1',
                'typedParam2': '2',
                'typedParam3': '3',
                'typedParam4': '4'
            }
        )
        self.assertEqual(type(resp.json['typedParam1']), float)
        self.assertEqual(type(resp.json['typedParam2']), float)
        self.assertEqual(type(resp.json['typedParam3']), float)
        self.assertEqual(type(resp.json['typedParam4']), str)

        self.wsgi_app.post(
            '/validation',
            params={'typedParam1': 'not_convertible'},
            status=400
        )

        # -----------------------------
        # role -> Client
        self.wsgi_app.extra_environ['fake_roles'] = 'client'
        resp = self.wsgi_app.post(
            '/validation',
            params={
                'typedParam1': '1',
                'typedParam2': '2',
                'typedParam3': '3',
                'typedParam4': '4'
            }
        )
        self.assertEqual(type(resp.json['typedParam1']), int)
        self.assertEqual(type(resp.json['typedParam2']), int)
        self.assertEqual(type(resp.json['typedParam3']), float)
        self.assertEqual(type(resp.json['typedParam4']), str)

        self.wsgi_app.post(
            '/validation',
            params={'typedParam1': 'not_convertible'},
            status=400
        )

        # -----------------------------
        # role -> Admin
        self.wsgi_app.extra_environ['fake_roles'] = 'admin'
        resp = self.wsgi_app.post(
            '/validation',
            params={
                'typedParam1': '1',
                'typedParam2': '2',
                'typedParam3': '3',
                'typedParam4': '4'
            }
        )
        # type complex is dict
        self.assertEqual(type(resp.json['typedParam1']), dict)
        self.assertEqual(type(resp.json['typedParam2']), float)
        self.assertEqual(type(resp.json['typedParam3']), float)
        self.assertEqual(type(resp.json['typedParam4']), dict)

        self.wsgi_app.post(
            '/validation',
            params={'typedParam1': 'not_convertible'},
            status=400
        )


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
