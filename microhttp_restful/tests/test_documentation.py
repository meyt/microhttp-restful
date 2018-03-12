import unittest

from nanohttp import json

from microhttp.ext import db
from webtest_docgen import TestDocumentApp, DocumentationRoot, Resource, UriParam

from microhttp_restful.controllers import RestController, RootController
from microhttp_restful.tests.helpers import WebAppTestCase, WebTestMetaDataMixin
from microhttp_restful.tests.test_base_model import Member


class MemberController(RestController):

    @json
    @db.commit
    def post(self):
        db_session = db.get_session()
        m = Member()
        m.keywords.append('Hello')
        m.update_from_request()
        db_session.add(m)
        return m

    @json
    @db.commit
    def put(self, member_id: int):
        db_session = db.get_session()
        m = db_session.query(Member).get(member_id)
        m.update_from_request()
        return m

    @json
    @Member.expose
    def get(self, title: str=None):
        query = Member.query
        if title:
            return query.filter(Member.title == title).one_or_none()
        return query


class Root(RootController):
    member = MemberController()


class WebTestDocumentationApp(TestDocumentApp, WebTestMetaDataMixin):
    pass


class DocumentationTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()
        cls.docs_root = DocumentationRoot(
            title='MyTestApp'
        )
        cls.wsgi_doc_app = WebTestDocumentationApp(
            app=cls.application,
            docs_root=cls.docs_root
        )

    def test_documentation(self):
        # Register models
        self.docs_root.set_resources(
            Resource(
                path='/member',
                method='get'
            ),
            Resource(
                path='/member/{member_id}',
                method='get',
                params=UriParam(
                    name='member_id',
                    type_='integer'
                )
            ),
            Resource(
                path='/member/{member_id}',
                method='put',
                params=[UriParam(
                    name='member_id',
                    type_='integer'
                )] + list(Member.to_form_params())
            ),
            Resource(
                path='/member',
                method='post',
                params=Member.to_form_params()
            )
        )

        resp_member_one = self.wsgi_doc_app.post('/member', params={
            'title': 'test',
            'firstName': 'test',
            'lastName': 'test',
            'email': 'test@example.com',
            'password': '123456',
            'birth': '2001-01-01',
            'weight': 1.1,
            'visible': 'false',
            'myType': 'Test',
            'lastLoginTime': '2017-10-10T15:44:30.000',
            'isActive': True
        })
        self.wsgi_doc_app.get('/member')
        self.wsgi_doc_app.get('/member/test')

        self.wsgi_doc_app.put('/member/%s' % resp_member_one.json['id'], params={
            'weight': 1.5
        })


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
