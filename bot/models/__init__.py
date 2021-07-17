from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
import psycopg2

ENGINE = create_engine("postgresql://ruby@Malassi12:5433/grace_development")
BASE = declarative_base()
