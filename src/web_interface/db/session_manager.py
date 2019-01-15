#! /usr/bin/python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from db.db_config import DB_CONFIG

Base = declarative_base()


class SessionManager(object):
    """Handle DB sessions"""

    def __init__(self):
        self._engine = create_engine(DB_CONFIG.connection_uri,
                                     echo=DB_CONFIG.log)
        Base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(bind=self._engine)
        self._session = None

    def __enter__(self):
        assert self._session is None
        self._session = self._session_factory()
        return self._session

    def __exit__(self, type, value, traceback):
        assert self._session is not None
        self._session.close()
        self._session = None


def main(argv):
    session_mgr = SessionManager()
    with session_mgr:
        pass


if __name__ == "__main__":
    import sys
    main(sys.argv)
