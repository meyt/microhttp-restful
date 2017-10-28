import unittest
from datetime import datetime

from sqlalchemy import Integer, Unicode, DateTime
from nanohttp import json

from microhttp.ext import db
from microhttp_restful import Field
from microhttp_restful.controllers import ModelRestController, JsonPatchControllerMixin
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import DeclarativeBase


class ModelValidationCheckingModel(DeclarativeBase):
    __tablename__ = 'model_validation_checking_model'

    id = Field(Integer, primary_key=True, readonly=True)
    title = Field(Unicode(50), unique=True, nullable=False, pattern='[A-Z][a-zA-Z]*')
    modified = Field(DateTime, default=datetime.now, readonly=True)


class Root(JsonPatchControllerMixin, ModelRestController):
    __model__ = ModelValidationCheckingModel

    @ModelValidationCheckingModel.validate
    @json
    @db.commit
    def post(self):
        db_session = db.get_session()
        m = ModelValidationCheckingModel()
        m.update_from_request()
        db_session.add(m)
        return m


class ModelValidationDecoratorTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()

    def test_model_validate_decorator(self):
        # Required
        self.wsgi_app.post('/', params={}, status=400)

        # Correct pattern
        resp = self.wsgi_app.post('/', params=dict(title='Test'))
        self.assertEqual(resp.json['title'], 'Test')

        # Invalid pattern
        self.wsgi_app.post('/', params=dict(title='startWithSmallCase'), status=400)

        # Readonly
        self.wsgi_app.post('/', params=dict(
            title='Test',
            modified=datetime.now().isoformat()
        ), status=400)

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
