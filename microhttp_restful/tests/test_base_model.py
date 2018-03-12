import unittest

from sqlalchemy import Integer, Unicode, ForeignKey, Boolean, Date, DateTime, Float, TypeDecorator
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import synonym

from nanohttp import json

from microhttp.ext import db
from microhttp_restful import (
    ActivationMixin,
    ModifiedMixin,
    FilteringMixin,
    PaginationMixin,
    OrderingMixin,
    Field,
    composite,
    relationship
)
from microhttp_restful.controllers import JsonPatchControllerMixin, ModelRestController
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import DeclarativeBase


# noinspection PyAbstractClass
class MyType(TypeDecorator):
    impl = Unicode

    def process_bind_param(self, value, dialect):
        return "PREFIX:" + value

    def process_result_value(self, value, dialect):
        return value[7:]


class FullName(object):  # pragma: no cover
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def __composite_values__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def __repr__(self):
        return "FullName(%s %s)" % (self.first_name, self.last_name)

    def __eq__(self, other):
        return isinstance(other, FullName) and \
               other.first_name == self.first_name and \
               other.last_name == self.last_name

    def __ne__(self, other):
        return not self.__eq__(other)


class Keyword(DeclarativeBase):
    __tablename__ = 'keyword'
    id = Field(Integer, primary_key=True)
    keyword = Field(Unicode(64))


class MemberKeywords(DeclarativeBase):
    __tablename__ = 'member_keywords'
    member_id = Field(Integer, ForeignKey("member.id"), primary_key=True)
    keyword_id = Field(Integer, ForeignKey("keyword.id"), primary_key=True)


class Member(ActivationMixin, ModifiedMixin, FilteringMixin, PaginationMixin, OrderingMixin, DeclarativeBase):
    __tablename__ = 'member'

    id = Field(Integer, primary_key=True)
    email = Field(Unicode(100), unique=True, index=True,
                  pattern=r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', watermark='Email',
                  example="user@example.com", message='Invalid email address, please be accurate!', icon='email.svg')
    title = Field(Unicode(50), index=True, min_length=2, watermark='First Name')
    first_name = Field(Unicode(50), index=True, min_length=2, watermark='First Name')
    last_name = Field(Unicode(100), min_length=2, watermark='Last Name')
    phone = Field(
        Unicode(10), nullable=True, min_length=10,
        pattern=r'\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}',
        watermark='Phone'
    )
    name = composite(FullName, first_name, last_name, readonly=True, json='fullName')
    _password = Field('password', Unicode(128), index=True, dict_key='password', protected=True, min_length=6)
    birth = Field(Date)
    weight = Field(Float(asdecimal=True), default=50)
    _keywords = relationship('Keyword', secondary='member_keywords')
    keywords = association_proxy('_keywords', 'keyword', creator=lambda k: Keyword(keyword=k))
    visible = Field(Boolean, nullable=True)
    last_login_time = Field(DateTime)
    my_type = Field(MyType)

    def _set_password(self, password):
        self._password = 'hashed:%s' % password

    def _get_password(self):  # pragma: no cover
        return self._password

    password = synonym('_password', descriptor=property(_get_password, _set_password), info=dict(protected=True))

    @hybrid_property
    def is_visible(self):
        return 'yes' if self.visible else 'no'


class Root(JsonPatchControllerMixin, ModelRestController):
    __model__ = Member

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
    @Member.expose
    def get(self, title: str=None):
        query = Member.query
        if title:
            return query.filter(Member.title == title).one_or_none()
        return query

    @json
    @Member.expose
    def me(self):
        return dict(
            title='me'
        )

    @json
    @Member.expose
    def empty(self, empty_list: bool=None):
        return list() if empty_list else None


class BaseModelTestCase(WebAppTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.application.__root__ = Root()

    def test_update_from_request(self):
        resp = self.wsgi_app.post(
            '/',
            params={
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
            }
        )
        self.assertEqual(resp.json['title'], 'test')

        resp = self.wsgi_app.get(
            '/',
            params=dict(take=1)
        )
        self.assertEqual(len(resp.json), 1)
        self.assertEqual(resp.json[0]['title'], 'test')
        self.assertEqual(resp.json[0]['visible'], False)

        # 404
        self.wsgi_app.get(
            '/non-existence-user',
            status=404
        )

        # Plain dictionary
        resp = self.wsgi_app.get(
            '/me'
        )
        self.assertEqual(resp.json['title'], 'me')

        # Get columns in FormParameter list
        self.assertEqual(len(list(Member.to_form_params())), 11)

        # Should return empty list
        self.wsgi_app.get('/empty/true', status=200)
        self.wsgi_app.get('/empty', status=404)

    def test_metadata(self):
        resp = self.wsgi_app.metadata('/')

        self.assertIn('fields', resp.json)
        self.assertIn('name', resp.json)
        self.assertIn('primaryKeys', resp.json)
        self.assertIn('id', resp.json['primaryKeys'])
        self.assertEqual(resp.json['name'], 'Member')
        fields = resp.json['fields']
        self.assertIn('id', fields)
        self.assertIn('firstName', fields)
        self.assertEqual(fields['id']['primaryKey'], True)
        self.assertEqual(fields['email']['primaryKey'], False)
        self.assertEqual(fields['title']['primaryKey'], False)
        self.assertEqual(fields['title']['minLength'], 2)
        self.assertEqual(fields['title']['maxLength'], 50)
        self.assertEqual(fields['email']['pattern'], '(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')

        self.assertEqual(fields['firstName']['name'], 'firstName')
        self.assertEqual(fields['firstName']['key'], 'first_name')

        self.assertEqual(fields['firstName']['type_'], 'str')
        self.assertEqual(fields['birth']['type_'], 'date')

        self.assertEqual(fields['weight']['default'], 50)
        self.assertEqual(fields['visible']['optional'], True)

        self.assertEqual(fields['email']['message'], 'Invalid email address, please be accurate!')
        self.assertEqual(fields['email']['watermark'], 'Email')
        self.assertEqual(fields['email']['label'], 'Email')
        self.assertEqual(fields['email']['icon'], 'email.svg')
        self.assertEqual(fields['email']['example'], 'user@example.com')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
