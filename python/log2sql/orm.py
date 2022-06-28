"""This is the primary database interface for log2sql using SQLAlchemy.

This module is intended to serve as a generic python `CRUD` interface and should remain decoupled
from everything else.

To replace with your own backend just keep the below method signatures intact.
"""
import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database


class ORM(object):
    """Manage the connection to backend and facilitate `CRUD` operations.

    This Class is meant to serve as an adapter to any backend in case a different one is desired.
    DB connection settings and credentials should also be managed here.
    """
    CONFIG = {
        "dialect": "sqlite",
        "username": os.getenv("LOG2SQLITE_DB_USERNAME"),
        "password": os.getenv("LOG2SQLITE_DB_PASSWORD"),
        "hostname": os.getenv("LOG2SQLITE_DB_HOSTNAME"),
        "port": os.getenv("LOG2SQLITE_DB_PORT"),
        "db_name": os.getenv("LOG2SQLITE_DB_NAME"),
        "data_dir": os.getenv("LOG2SQLITE_DB_DATA_DIR"),
        "sqlite_check_same_thread": False,
        "log_level": os.getenv("LOG2SQLITE_LOG_LEVEL", logging.DEBUG)
    }
    BASE = declarative_base()
    SESSION = None
    ENGINE = None
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(CONFIG["log_level"])

    def __init__(self):
        """Instantiate and iniliatize DB tables."""
        self._session = None

    def connect(self):
        """Perform `SQLAlchemy` initializations, create filesystem directory for `sqlite` data."""
        self._construct_engine()
        if not os.path.isdir(self.CONFIG["data_dir"]):
            os.makedirs(self.CONFIG["data_dir"])
        if not database_exists(self.ENGINE.url):
            self.LOGGER.warning("No database found at: {db}".format(db=self.ENGINE.url))
            self.LOGGER.warning("creating [{dialect}]: {db}".format(dialect=self.CONFIG["dialect"], db=self.ENGINE.url))
            create_database(self.ENGINE.url)
        self._construct_session()
        self._create_all_tables()
        self._session = self.SESSION()
    
    def disconnect(self):
        self.session.close()

    @property
    def session(self):
        """Retrieve Session class or Session Instance (after `_construct_session` has been called).

        Returns
        -------
        sqlalchemy.orm.Session
            Session class/object
        """
        return self._session

    @classmethod
    def _create_all_tables(cls):
        """Create all tables currently defined in metadata."""
        result = cls.BASE.metadata.create_all(cls.ENGINE)
        cls.LOGGER.warning("creating tables: {result}".format(result=result))

    @classmethod
    def _drop_all_tables(cls):
        """Drop all tables currently defined in metadata."""
        cls.BASE.metadata.drop_all(bind=cls.ENGINE)
        cls.LOGGER.warning("Dropping all tables for session: {session}".format(session=cls.SESSION))

    @classmethod
    def _construct_session(cls, *args, **kwargs):
        """Construct session-factory."""
        # TODO: include test coverage for constructing sessions with args/kwargs
        cls.SESSION = cls.sessionmaker(*args, **kwargs)
        cls.LOGGER.info("Session created: {session}".format(session=cls.SESSION))

    @classmethod
    def _construct_engine(cls):
        """Construct a `SQLAlchemy` engine of the type currently set in `CONFIG['dialect']`.""" 
        engine_constructor_callable = getattr(
            cls,
            "_construct_{dialect}ENGINE".format(dialect=cls.CONFIG["dialect"]),
            cls._construct_sqlite_engine  # <--Defaults to SQLite
        )
        engine_constructor_callable()
        cls.LOGGER.info("Engine constructed: {engine}".format(engine=cls.ENGINE))

    @classmethod
    def _construct_sqlite_engine(cls):
        """Construct the engine to be used by `SQLAlchemy`."""
        cls.ENGINE = create_engine(
            "sqlite:///{data_dir}/{db_name}?check_same_thread={sqlite_check_same_thread}".format(**cls.CONFIG)
        )

    @classmethod
    def _construct_postgres_engine(cls):
        """Construct the engine to be used by `SQLAlchemy`."""
        cls.ENGINE = create_engine(
            "postgresql://{username}:{password}@{hostname}:{port}/{db_name}".format(**cls.CONFIG)
        )

    @classmethod
    def sessionmaker(cls, **kwargs):
        """Create new session factory.

        Returns
        -------
        sqlalchemy.orm.sessionmaker
            Session factory
        """
        return sessionmaker(bind=cls.ENGINE, **kwargs)

    def _query(self, entity, **filter_kwargs):
        """Query the `SQLAlchemy` session for given entity and data.

        Parameters
        ----------
        entity : magla.core.entity.MaglaEntity
            The sub-entity to be queried

        Returns
        -------
        sqlalchemy.ext.declarative.api.Base
            The returned record from the session query (containing data directly from backend)
        """
        return self.session.query(entity).filter_by(**filter_kwargs)

    def get_model(self, table_name):
        return self.BASE._decl_class_registry.get(table_name)

    def create(self, entity, data, return_existing=False):
        """Create the given entity type using given data.

        Parameters
        ----------
        entity : magla.core.entity.MaglaEntity
            The entity type to create
        data : dict
            A dictionary containing data to create new record with
        return_existing : bool
            flag to first perform query to see if matching record already exists, and return early

        Returns
        -------
        magla.core.entity.MaglaEntity
            A `MaglaEntity` from the newly created record
        """
        if return_existing:
            qresult = self.query(entity, data)
            if qresult.count():
                existing_record = qresult.first()
                self.LOGGER.warning("`return_existing` flag set, returning existing record: {existing_record}".format(existing_record=existing_record))
                return existing_record

        # create new record with given data
        new_entity_record = entity(**data)
        try:
            self.session.add(new_entity_record)
            self.session.commit()
        except Exception as err:
            print(err.__class__.__name__)
        self.LOGGER.info("Creating {}".format(new_entity_record))
        self.LOGGER.debug(new_entity_record.__dict__)
        return new_entity_record

    def delete(self, entity):
        """Delete the given entity.

        Parameters
        ----------
        entity : sqlalchemy.ext.declarative.api.Base
            The `SQLAlchemy` mapped entity object to drop
        """
        self.session.delete(entity)
        self.session.commit()

    def query(self, entity, data=None, **filter_kwargs):
        """Query the `SQLAlchemy` session for given entity type and data/kwargs.

        Parameters
        ----------
        entity : magla.core.entity.MaglaEntity
            The sub-class of `MaglaEntity` to query
        data : dict, optional
            A dictionary containing the data to query for, by default None

        Returns
        -------
        sqlalchemy.orm.query.Query
            The `SQAlchemy` query object containing results
        """
        data = data or {}
        data.update(dict(filter_kwargs))
        self.LOGGER.info("Querying for: {}".format(data))
        self.LOGGER.debug(data)
        return self._query(entity, **data)
