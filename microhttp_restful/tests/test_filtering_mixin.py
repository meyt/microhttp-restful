import unittest

from datetime import datetime, timezone, timedelta

from sqlalchemy import Integer, Unicode, DateTime

from nanohttp import HTTPBadRequest
from nanohttp.contexts import Context

from microhttp.ext import db
from microhttp_restful import FilteringMixin, Field
from microhttp_restful.tests.helpers import WebAppTestCase
from microhttp_restful.tests.helpers import DeclarativeBase


class FilteringObject(FilteringMixin, DeclarativeBase):
    __tablename__ = 'filtering_object'

    id = Field(Integer, primary_key=True)
    title = Field(Unicode(50))
    updated_at = Field(DateTime, nullable=True)


class FilteringMixinTestCase(WebAppTestCase):

    def test_filtering_mixin(self):
        db_session = db.get_session()
        for i in range(1, 6):
            # noinspection PyArgumentList
            obj = FilteringObject(
                title='object %s' % i,
                updated_at=datetime(2010, 10, 10, 12, 12, 12, 300)
            )
            db_session.add(obj)
        db_session.commit()

        # Bad Value
        with Context({'QUERY_STRING': 'id=1'}, self.application) as context:
            context.query['id'] = 1
            self.assertRaises(HTTPBadRequest, FilteringObject.filter_by_request)

        with Context({'QUERY_STRING': 'id=1&id=2'}, self.application):
            self.assertRaises(HTTPBadRequest, FilteringObject.filter_by_request)

        # IN
        with Context({'QUERY_STRING': 'id=^1,2,3'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 3)

        # NOT IN
        with Context({'QUERY_STRING': 'id=!^1,2,3'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 2)

        # IN (error)
        with Context({'QUERY_STRING': 'id=^'}, self.application):
            self.assertRaises(HTTPBadRequest, FilteringObject.filter_by_request)

        # Between
        with Context({'QUERY_STRING': 'id=~1,3'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 3)

        # IS NULL
        with Context({'QUERY_STRING': 'title=null'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 0)

        # IS NOT NULL
        with Context({'QUERY_STRING': 'title=!null'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 5)

        # LIKE
        with Context({'QUERY_STRING': 'title=%obj'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 5)

        with Context({'QUERY_STRING': 'title=%OBJ'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 0)

        # ILIKE
        with Context({'QUERY_STRING': 'title=%~obj'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 5)

        with Context({'QUERY_STRING': 'title=%~OBJ'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 5)

        # ==
        with Context({'QUERY_STRING': 'id=1'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 1)

        # !=
        with Context({'QUERY_STRING': 'id=!1'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 4)

        # >=
        with Context({'QUERY_STRING': 'id=>=2'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 4)

        # >
        with Context({'QUERY_STRING': 'id=>2'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 3)

        # <=
        with Context({'QUERY_STRING': 'id=<=3'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 3)

        # <
        with Context({'QUERY_STRING': 'id=<3'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 2)

        # Date Time
        with Context({'QUERY_STRING': 'updatedAt=2010-10-10T12:12:12.000300'}, self.application):
            self.assertEqual(FilteringObject.filter_by_request().count(), 5)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
