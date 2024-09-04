from django.apps import apps
from timestamps.admin import get_table_last_updated,update_table_last_updated
from django.db import connection

# def update_timestamps_table(table_name:str, key:str):
#     if apps.is_installed("timestamps"):
#         from timestamps.admin import update_tables_last_updated
#         update_tables_last_updated(table_name, key)

def update_timestamps_table_lastupdated(table_name:str) -> str:
    if apps.is_installed("timestamps"):
        return update_table_last_updated(table_name)

def get_table_lastupdated_datetime(table_name:str) -> str:
    if apps.is_installed("timestamps"):
        return get_table_last_updated(table_name)
    
def update_tableA_FK_match_with_tableB_PK_on_matching_columns(table_a_name:str, table_b_name:str,a_foreignkey_column_name:str, b_primary_key_column_name:str, **kwargs):

    column_names = kwargs.get('table_a_to_table_b_columns', {})

    if not column_names:
        raise ValueError("'table_a_to_table_b_columns' must be provided")

    # Construct the WHERE clause for the SQL query
    where_clause_parts = []
    for table_a_col, table_b_col in column_names.items():
        where_clause_parts.append(f"{table_a_name}.{table_a_col} = b.{table_b_col}")
    where_clause = " AND ".join(where_clause_parts)

    # run query
    with connection.cursor() as cursor:
        cursor.execute(f"""
            UPDATE {table_a_name}
            SET {a_foreignkey_column_name} = b.{b_primary_key_column_name}
            FROM {table_b_name} b
            WHERE {where_clause}
        """)