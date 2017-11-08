from unittest import TestCase

from webtest import TestApp

from microhttp.ext import db
from microhttp_restful.tests.helpers import MockApplication, DeclarativeBase


class WebTestMetaDataMixin:

    def metadata(self, url, params='', headers=None, extra_environ=None,
                 status=None, upload_files=None, expect_errors=False,
                 content_type=None):
        # noinspection PyUnresolvedReferences
        return self._gen_request('METADATA', url, params=params, headers=headers,
                                 extra_environ=extra_environ, status=status,
                                 upload_files=upload_files,
                                 expect_errors=expect_errors,
                                 content_type=content_type)


class WebTestApp(TestApp, WebTestMetaDataMixin):
    pass


class WebAppTestCase(TestCase):
    application = None
    session = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application = MockApplication()
        cls.application.configure(force=True)
        cls.wsgi_app = WebTestApp(cls.application)
        cls.session = db.get_session()
        DeclarativeBase.metadata.create_all(bind=cls.session.get_bind())

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.session.close()
        cls.session.get_bind().dispose()
        with db.get_database_manager() as manager:
            manager.drop_database()
