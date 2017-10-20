#!/usr/bin/python
# coding: utf-8

"""
    author:     small 
    date:       17-3-25
    purpose:    
"""
import os
import json
import inspect
import traceback
import threading
import multiprocessing
from datetime import datetime
import logging


try:
    from sqlalchemy import create_engine, Column, not_
    from sqlalchemy import Integer, String, Boolean, DateTime, Enum, func, VARCHAR
    from sqlalchemy import ForeignKey, Text, Index, Table
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.exc import SQLAlchemyError, IntegrityError
    from sqlalchemy.orm import sessionmaker, relationship, joinedload
    from sqlalchemy.ext.hybrid import hybrid_property
    Base = declarative_base()
except ImportError:
    raise Exception(
        "Unable to import sqlalchemy (install with `pip install sqlalchemy`)"
    )

log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])


paper_tags_association = Table(
    'paper_tags_table',
    Base.metadata,
    Column('abstract_id', Integer, ForeignKey('paper_abstract.id')),
    Column('tag_id', Integer, ForeignKey('paper_tags.id'))
)


class PaperTags(Base):
    """tags table."""
    __tablename__ = "paper_tags"

    id = Column(Integer(), primary_key=True)
    tag_name = Column(VARCHAR(255), nullable=False)
    tag_url = Column(Text(), nullable=False)
    paper_id = relationship('PaperAbstract', secondary=paper_tags_association)

    def to_dict(self):
        """Converts object to dict.
        @return: dict
        """
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)
        return d

    def to_json(self):
        """Converts object to JSON.
        @return: JSON data
        """
        return json.dumps(self.to_dict())

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, list):
                value = json.dumps(value)
            setattr(self, key, value)


class PaperAbstract(Base):
    """spider_paper abstract table."""
    __tablename__ = "paper_abstract"

    id = Column(Integer(), primary_key=True)
    crawl_time = Column(DateTime(), nullable=False)
    paper_title = Column(Text(), nullable=False)
    paper_url = Column(VARCHAR(512), nullable=False, unique=True)
    author_name = Column(Text(), nullable=True)
    author_link = Column(Text(), nullable=True)
    author_identity = Column(Boolean(), nullable=True, default=False)
    paper_time = Column(Text(), nullable=True)
    paper_abstract = Column(Text(), nullable=True)
    paper_tags = relationship('PaperTags', secondary=paper_tags_association)
    paper_look_number = Column(Integer(), nullable=True)
    paper_look_comments = Column(Integer(), nullable=True)
    paper_spider = Column(Text(), nullable=True)
    paper_file = Column(Text(), nullable=True, default='')

    def to_dict(self):
        """Converts object to dict.
        @return: dict
        """
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)
        return d

    def to_json(self):
        """Converts object to JSON.
        @return: JSON data
        """
        return json.dumps(self.to_dict())

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def classlock(f):
    """Classlock decorator (created for database.Database).
    Used to put a lock to avoid sqlite errors.
    """
    def inner(self, *args, **kwargs):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)

        if calframe[1][1].endswith("db_base.py"):
            return f(self, *args, **kwargs)

        with self._lock:
            return f(self, *args, **kwargs)

    return inner


class Singleton(type):
    """Singleton.
    @see: http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SuperLock(object):
    def __init__(self):
        self.tlock = threading.Lock()
        self.mlock = multiprocessing.Lock()

    def __enter__(self):
        self.tlock.acquire()
        self.mlock.acquire()

    def __exit__(self, type, value, traceback):
        self.mlock.release()
        self.tlock.release()


class DataBase(object):
    """postgresql 数据库操作"""
    # __metaclass__ = Singleton

    def __init__(self, dsn=None, schema_check=True, echo=False):
        """
        @param dsn: database connection string.
        @param schema_check: disable or enable the db schema version check.
        @param echo: echo sql queries.
        """
        self._lock = SuperLock()

        if not dsn:
            dsn = "mysql://root:root@localhost/scrapy_paper?charset=utf8"
        self._connect_database(dsn)

        # Disable SQL logging. Turn it on for debugging.
        self.engine.echo = echo

        # Connection timeout.
        self.engine.pool_timeout = 60

        # Create schema.
        try:
            Base.metadata.create_all(self.engine)
        except SQLAlchemyError as e:
            raise SQLAlchemyError("Unable to create or connect to database: {0}".format(e))

        # Get db session.
        self.Session = sessionmaker(bind=self.engine)

    def __del__(self):
        """Disconnects pool."""
        try:
            self.engine.dispose()
        except Exception as e:
            pass

    def _connect_database(self, connection_string):
        """Connect to a Database.
        @param connection_string: Connection string specifying the database
        """
        try:
            # TODO: this is quite ugly, should improve.
            if connection_string.startswith("sqlite"):
                # Using "check_same_thread" to disable sqlite safety check on multiple threads.
                self.engine = create_engine(connection_string, connect_args={"check_same_thread": False})
            elif connection_string.startswith("postgres"):
                # Disabling SSL mode to avoid some errors using sqlalchemy and multiprocesing.
                # See: http://www.postgresql.org/docs/9.0/static/libpq-ssl.html#LIBPQ-SSL-SSLMODE-STATEMENTS
                self.engine = create_engine(connection_string, connect_args={"sslmode": "disable"})
            else:
                self.engine = create_engine(connection_string, encoding='utf-8', echo=True)
        except ImportError as e:
            lib = e.message.split()[-1]
            raise ImportError(
                "Missing database driver, unable to import %s (install with "
                "`pip install %s`)" % (lib, lib)
            )

    def _get_or_create(self, session, model, **kwargs):
        """Get an ORM instance or create it if not exist.
        @param session: SQLAlchemy session object
        @param model: model to query
        @return: row instance
        """
        instance = session.query(model).filter_by(**kwargs).first()
        return instance or model(**kwargs)

    @classlock
    def drop(self):
        """Drop all tables."""
        try:
            Base.metadata.drop_all(self.engine)
        except SQLAlchemyError as e:
            raise SQLAlchemyError("Unable to create or connect to database: {0}".format(e))

    def execute(self, sql):
        session = self.Session()
        try:
            session.execute(sql)
        except Exception as e:
            log.error("execute sql error: {0}".format(traceback.format_exc))
        finally:
            session.close()
        return session.execute(sql)

    def get_or_create_obj(self, session, obj, **args):
        db_obj = None
        try:
            db_obj = session.query(obj).filter_by(**args).first()
            if not db_obj:
                db_obj = obj(**args)
                session.add(db_obj)
                session.commit()
        except Exception as e:
            log.error("get_or_create_obj error: {0}".format(e))
        return db_obj

    def exist_sp_paper(self, **kwargs):
        session = self.Session()
        try:
            obj = session.query(PaperAbstract).filter_by(**kwargs)
            return obj.first()
        except Exception as e:
            log.error("exist_sp_paper error: {0}".format(traceback.format_exc))
        finally:
            session.close()

    def query_sp_paper(self, **kwargs):
        session = self.Session()
        try:
            rows = session.query(PaperAbstract).filter_by(**kwargs)
            return rows.all()
        except Exception as e:
            log.error("query_sp_paper error: {0}".format(traceback.format_exc))
        finally:
            session.close()

    def query_sp_paper_title(self):
        session = self.Session()
        try:
            rows = session.query(PaperAbstract.paper_title)
            return rows.all()
        except Exception as e:
            log.error("query_sp_paper_title error: {0}".format(e))
        finally:
            session.close()

    def up_sp_abstract(self, **abstract):
        return self.add_sp_abstract(update=True, **abstract)

    def add_sp_abstract(self, update=False, **abstract):
        session = self.Session()
        try:
            # if url not in database then add
            obj = session.query(PaperAbstract).filter(PaperAbstract.paper_url == abstract["paper_url"]).first()
            if obj and not update:
                return None

            if not obj:
                obj = PaperAbstract()

            for name, value in abstract.items():
                if name == 'paper_tags':
                    paper_tags = list()
                    for tag in value:
                        tag_obj = self.get_or_create_obj(session, PaperTags, **tag)
                        paper_tags.append(tag_obj)
                    abstract[name] = paper_tags
                elif name == 'paper_look_number' or name == 'paper_look_comments':
                    if value:
                        value = int(value)
                    else:
                        value = 0
                    abstract[name] = value
                elif isinstance(value, list):
                    abstract[name] = json.dumps(value)
            abstract["crawl_time"] = datetime.now()
            obj.__init__(**abstract)
            if not update:
                session.add(obj)
            session.commit()
        except Exception as e:
            error = traceback.format_exc()
            log.error("add_sp_abstract error: {0}".format(error))
        finally:
            session.close()
