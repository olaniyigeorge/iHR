
import databases
import sqlalchemy

from config import config

metadata = sqlalchemy.MetaData()


engine = sqlalchemy.create_engine(
    config.DATABASE_URL, connect_args={"check_same_thread: False"}
    )




metadata.create_all(engine)

database = databases.Database(
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLLBACK
)
