from nanohttp import settings


from microhttp.ext import db

from sqlalchemy.sql.schema import MetaData
from sqlalchemy.ext.declarative import declarative_base

from microhttp_restful import BaseModel, Application

metadata = MetaData()
DeclarativeBase = declarative_base(cls=BaseModel, metadata=metadata)


# noinspection PyAbstractClass
class MockApplication(Application):
    __configurations__ = '''
        ### nanohttp
        debug: true
        
        cookie:
          http_only: false
          secure: false
        json:
          indent: 0
        
        ### microhttp.ext.db
        sqlalchemy:
          default:
            admin_db_url: postgresql://postgres:postgres@localhost/postgres
            engine:
              name_or_url: postgresql://postgres:postgres@localhost/microhttp_restful
              echo: false
            session:
              autoflush: False
              autocommit: False
              expire_on_commit: True
              twophase: False
    '''

    def configure(self, files=None, context=None, **kwargs):
        super().configure(files=None, context=None, **kwargs)
        settings.merge(self.__configurations__)

        with db.get_database_manager() as manager:
            manager.drop_database()
            manager.create_database()

        db.configure()
        # noinspection PyUnresolvedReferences
        DeclarativeBase.query = db.get_session().query_property()
