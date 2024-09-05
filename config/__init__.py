# pg_dump args | pg_restore args

# pg_dump -U benjyongzh -d hdb-info -F tar -f ./db-backup.tar

# pg_restore -U benjyongzh -c -C --if-exists -d postgres -v ./db-backup.tar

# your_project/__init__.py
from .celery import app as celery_app

__all__ = ('celery_app',)
