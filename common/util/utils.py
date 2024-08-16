from django.apps import apps

# def update_timestamps_table(table_name:str, key:str):
#     if apps.is_installed("timestamps"):
#         from timestamps.admin import update_tables_last_updated
#         update_tables_last_updated(table_name, key)

def update_timestamps_table_lastupdated(table_name:str) -> str:
    if apps.is_installed("timestamps"):
        from timestamps.admin import update_table_last_updated
        return update_table_last_updated(table_name)

def get_table_lastupdated_datetime(table_name:str) -> str:
    if apps.is_installed("timestamps"):
        from timestamps.admin import get_table_last_updated
        return get_table_last_updated(table_name)