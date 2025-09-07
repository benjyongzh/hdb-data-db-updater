import os
import psycopg2


def db_postgres_conn():
    """Return a psycopg2 connection using a single DB_URL.

    Accepts standard libpq URLs, e.g.:
    - postgresql://user:pass@host:5432/dbname
    - postgres://user:pass@host:5432/dbname

    For backward compatibility, if DB_URL is not set, falls back to
    DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD to build a URL.
    """
    url = os.environ.get("DB_URL")
    if not url:
        host = os.environ.get("DB_HOST", "localhost")
        port = os.environ.get("DB_PORT", "5432")
        db = os.environ.get("DB_NAME", "postgres")
        user = os.environ.get("DB_USER", "postgres")
        password = os.environ.get("DB_PASSWORD", "")
        url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return psycopg2.connect(url)
