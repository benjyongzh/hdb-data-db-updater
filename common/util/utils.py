
from django.apps import apps

# def update_timestamps_table(table_name:str, key:str):
#     if apps.is_installed("timestamps"):
#         from timestamps.admin import update_tables_last_updated
#         update_tables_last_updated(table_name, key)

def update_timestamps_table_lastupdated(table_name:str):
    if apps.is_installed("timestamps"):
        from timestamps.admin import update_tables_last_updated
        update_tables_last_updated(table_name)