import unittest
from datetime import date, time

from sqlalchemy import Integer, Unicode, ForeignKey, Boolean, Table, Date, Time, Float
from sqlalchemy.orm import synonym

from nanohttp import HttpBadRequest

from microhttp.ext import db
from microhttp_restful import ModifiedMixin, Field, composite, relationship
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import DeclarativeBase


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


class Author(DeclarativeBase):
    __tablename__ = 'author'

    id = Field(Integer, primary_key=True)
    email = Field(Unicode(100), unique=True, index=True,
                  pattern=r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', watermark='Email',
                  example="user@example.com")
    title = Field(Unicode(50), index=True, min_length=2, watermark='First Name')
    first_name = Field(Unicode(50), index=True, min_length=2, watermark='First Name')
    last_name = Field(Unicode(100), min_length=2, watermark='Last Name')
    phone = Field(
        Unicode(10), nullable=True, min_length=10,
        pattern=r'\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}',
        watermark='Phone'
    )
    name = composite(FullName, first_name, last_name, readonly=True, dict_key='fullName', protected=True)
    _password = Field('password', Unicode(128), index=True, dict_key='password', protected=True, min_length=6)
    birth = Field(Date)
    weight = Field(Float(asdecimal=True))

    def _set_password(self, password):
        self._password = 'hashed:%s' % password

    def _get_password(self):  # pragma: no cover
        return self._password

    password = synonym('_password', descriptor=property(_get_password, _set_password), info=dict(protected=True))


class Memo(DeclarativeBase):
    __tablename__ = 'memo'
    id = Field(Integer, primary_key=True)
    content = Field(Unicode(100), max_length=90)
    post_id = Field(ForeignKey('post.id'))


class Comment(DeclarativeBase):
    __tablename__ = 'comment'
    id = Field(Integer, primary_key=True)
    content = Field(Unicode(100), max_length=90)
    special = Field(Boolean, default=True)
    post_id = Field(ForeignKey('post.id'))
    post = relationship('Post')


post_tag_table = Table(
    'post_tag', DeclarativeBase.metadata,
    Field('post_id', Integer, ForeignKey('post.id')),
    Field('tag_id', Integer, ForeignKey('tag.id'))
)


class Tag(DeclarativeBase):
    __tablename__ = 'tag'
    id = Field(Integer, primary_key=True)
    title = Field(Unicode(50), watermark='title', label='title')
    posts = relationship('Post', secondary=post_tag_table, back_populates='tags')


class Post(ModifiedMixin, DeclarativeBase):
    __tablename__ = 'post'

    id = Field(Integer, primary_key=True)
    title = Field(Unicode(50), watermark='title', label='title', icon='star')
    author_id = Field(ForeignKey('author.id'))
    author = relationship(Author)
    memos = relationship(Memo, protected=True)
    comments = relationship(Comment)
    tags = relationship(Tag, secondary=post_tag_table, back_populates='posts')
    tag_time = Field(Time)


class ORMTestCase(WebAppTestCase):

    def test_orm(self):
        db_session = db.get_session()
        # noinspection PyArgumentList
        author1 = Author(
            title='author1',
            email='author1@example.org',
            first_name='author 1 first name',
            last_name='author 1 last name',
            phone=None,
            password='123456',
            birth=date(1, 1, 1),
            weight=1.1
        )

        # noinspection PyArgumentList
        post1 = Post(
            title='First post',
            author=author1,
            tag_time=time(1, 1, 1)
        )
        db_session.add(post1)
        db_session.commit()

        self.assertEqual(post1.id, 1)

        # Validation, Type
        with self.assertRaises(HttpBadRequest):
            Author(title=234)

        # Validation, Pattern
        with self.assertRaises(HttpBadRequest):
            Author(email='invalidEmailAddress')

        # Validation, Min length
        with self.assertRaises(HttpBadRequest):
            Author(title='1')

        # Validation, Max length
        # Validation, Max length
        with self.assertRaises(HttpBadRequest):
            Author(phone='12321321321312321312312')

        # Metadata
        author_metadata = Author.json_metadata()
        self.assertIn('id', author_metadata['fields'])
        self.assertIn('email', author_metadata['fields'])
        self.assertEqual(author_metadata['fields']['fullName']['protected'], True)
        self.assertEqual(author_metadata['fields']['password']['protected'], True)

        post_metadata = Post.json_metadata()
        self.assertIn('author', post_metadata['fields'])

        comment_metadata = Comment.json_metadata()
        self.assertIn('post', comment_metadata['fields'])

        tag_metadata = Tag.json_metadata()
        self.assertIn('posts', tag_metadata['fields'])

        self.assertEqual(Comment.import_value(Comment.__table__.c.special, 'TRUE'), True)

        post1_dict = post1.to_dict()

        self.assertTrue(
            all(item in post1_dict.items() for item in {
                'author': {
                    'email': 'author1@example.org',
                    'firstName': 'author 1 first name',
                    'id': 1,
                    'lastName': 'author 1 last name',
                    'phone': None,
                    'title': 'author1',
                    'birth': '0001-01-01',
                    'weight': '1.1000000000'
                },
                'authorId': 1,
                'comments': [],
                'id': 1,
                'tags': [],
                'title': 'First post',
                'tagTime': '01:01:01'
            }.items())
        )
        self.assertIn('createdAt', post1_dict)
        self.assertIn('modifiedAt', post1_dict)

        author1_dict = author1.to_dict()
        self.assertNotIn('fullName', author1_dict)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
