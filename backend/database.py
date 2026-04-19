from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Update this to match your PostgreSQL setup
# Format: postgresql://username:password@localhost:5432/database_name
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:pradeepan5525@localhost:5432/sales_db"

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
try:
    con = psycopg2.connect(dbname='postgres', user='postgres', host='localhost', password='pradeepan5525')
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute('CREATE DATABASE sales_db')
    cur.close()
    con.close()
except Exception as e:
    pass # Ignore if it already exists

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
