
from django.apps import apps

def update_timestamps_table(table_name:str, key:str):
    if apps.is_installed("timestamps"):
        from timestamps.admin import update_table_timestamp
        update_table_timestamp(table_name, key)

def update_timestamps_table_lastupdated(table_name:str):
    update_timestamps_table(table_name, 'last_updated')