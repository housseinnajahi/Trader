from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .settings.postgres_settings import postgres_settings


class Postgres:
    def __init__(self):
        self.engine = create_engine(postgres_settings.DATABASE_URL)
        self.sessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.base = declarative_base()

    def get_db(self):
        try:
            yield self.sessionLocal()
        finally:
            self.sessionLocal().close()


postgres = Postgres()
