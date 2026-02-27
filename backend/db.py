import os
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/logs"
)

engine = create_engine(DATABASE_URL)


@event.listens_for(engine, "connect")
def _register_vector(dbapi_connection, connection_record):
    register_vector(dbapi_connection, arrays=True)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    return SessionLocal()

def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP,
            level TEXT,
            service TEXT,
            message TEXT,
            embedding vector(1536)
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS deployments (
            id SERIAL PRIMARY KEY,
            service TEXT,
            version TEXT,
            deployed_at TIMESTAMP
        );
        """))

        conn.commit()