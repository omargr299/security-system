
import sqlalchemy as sa
from sqlalchemy.orm import Session
from os import getenv
from dotenv import load_dotenv

load_dotenv()


def create_session(user, password):

    DATABASE_URI = f"postgresql+psycopg2://{user}:{password}@{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"
    engine = sa.create_engine(DATABASE_URI, echo=True)
    return Session(bind=engine)
