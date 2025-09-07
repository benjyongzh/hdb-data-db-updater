import os
import psycopg2


def db_postgres_conn():
    host = os.environ.get("DB_HOST", "localhost")
    port = int(os.environ.get("DB_PORT", "5432"))
    db = os.environ.get("DB_NAME", "postgres")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "")
    return psycopg2.connect(
        host=host, port=port, dbname=db, user=user, password=password
    )
