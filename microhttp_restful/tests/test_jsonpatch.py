import ujson
import unittest

from nanohttp import context, json, text, RestController
from nanohttp.contexts import Context

from microhttp_restful.controllers import JsonPatchControllerMixin
from microhttp_restful.tests.helpers import WebAppTestCase


class BiscuitsController(RestController):
    @json
    def put(self, id_: int = None):
        result = {}
        result.update(context.form)
        result['id'] = id_
        return result

    @json
    def get(self, id_: int = None):
        result = {}
        result.update(context.form)
        result['id'] = id_
        return result

    @json
    def error(self):
        raise Exception()


class SimpleJsonPatchController(JsonPatchControllerMixin, RestController):
    biscuits = BiscuitsController()

    @text
    def get(self):
        yield 'hey'
        yield 'you'


class JsonPatchTestCase(WebAppTestCase):

    def test_jsonpatch_rfc6902(self):
        environ = {
            'REQUEST_METHOD': 'PATCH'
        }
        with Context(environ):
            controller = SimpleJsonPatchController()
            context.form = [
                {"op": "get", "path": "/"},
                {"op": "put", "path": "biscuits/1", "value": {"name": "Ginger Nut"}},
                {"op": "get", "path": "biscuits/2", "value": {"name": "Ginger Nut"}},
            ]
            result = ujson.loads(controller())
            self.assertEqual(len(result), 3)

    def test_jsonpatch_error(self):
        environ = {
            'REQUEST_METHOD': 'PATCH'
        }
        with Context(environ):
            controller = SimpleJsonPatchController()
            context.form = [
                {"op": "put", "path": "biscuits/1", "value": {"name": "Ginger Nut"}},
                {"op": "error", "path": "biscuits", "value": None},
            ]
            self.assertRaises(Exception, controller)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
