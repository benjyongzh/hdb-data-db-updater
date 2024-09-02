
import psycopg2
from common.util.get_latest_file_in_folder import get_latest_file_in_folder
from config.env import env
import pandas as pd
from sqlalchemy import create_engine,types
from sqlalchemy.sql import text
from postalcodes.util.postal_codes import get_postal_code_from_address, create_postalcode_object
from postalcodes.models import PostalCodeAddress
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from typing import List
from resaletransactions.models import ResaleTransaction
from django.db import transaction


def update_resaletransactions_table_with_csv(table_name,csv_file,tmp_table_name:str) -> None:

    # get db connection
    db_connection_url = f"postgresql://{env('DB_USER')}:{env('DB_PASSWORD')}@{env('DB_HOST')}:{env('DB_PORT')}/{env('DB_NAME')}"
    engine = create_engine(db_connection_url)

    # copy pandas dataframe to temp table. csv file must have id column as primary key
    dataframe = pd.read_csv(csv_file)
    dataframe.to_sql(tmp_table_name, engine, if_exists='replace', index=False, chunksize=50000)

    connection = engine.connect()
    connection.execute(text(f"INSERT INTO {table_name} SELECT * FROM {tmp_table_name} ON CONFLICT DO NOTHING;"))
    connection.execute(text(f"DROP TABLE {tmp_table_name};"))
    connection.commit()
    connection.close()

def set_primary_key(engine, table_name:str, pk_column_name: str):
    with engine.connect() as conn:
        conn.execute(f"ALTER TABLE {table_name} ADD PRIMARY KEY({pk_column_name});")

def set_foreign_key(engine, table_name:str, fk_column_name:str, fk_ref_table_name:str, fk_ref_col_name:str):
    with engine.connect() as conn:
        conn.execute(f"ALTER TABLE {table_name} ADD FOREIGN KEY({fk_column_name}) REFERENCES {fk_ref_table_name}({fk_ref_col_name});")

def update_resaletransactions_foreignkey_on_postalcodes(batch_size) -> None:
    # cycle through related_model objects
    rows_to_update = ResaleTransaction.objects.filter(postal_code_id_id__isnull=True)

    postalcodes_addresses = PostalCodeAddress.objects.all()

    # get key pairs for block + street_name versus ID
    block_streetname_to_postalcode = {
        (entry.block, entry.street_name): entry.id
        for entry in postalcodes_addresses
    }

    for offset in range(0, len(rows_to_update), batch_size):
        # Fetch a batch of TableA records
        batch = rows_to_update[offset:offset + batch_size]
        
        # Collect instances to update
        to_update = []
        for resaletransaction_row in batch:
            key = (resaletransaction_row.block, resaletransaction_row.street_name)
            if key in block_streetname_to_postalcode:
                resaletransaction_row.postal_code_id_id = block_streetname_to_postalcode[key]
                to_update.append(resaletransaction_row)
                print(f"To update resale transactions' postalcode for {resaletransaction_row.block} {resaletransaction_row.street_name} with foreign key {block_streetname_to_postalcode[key]}")

        # Perform the bulk update for the batch
        if to_update:
            with transaction.atomic():
                ResaleTransaction.objects.bulk_update(to_update, ['postal_code_id_id'])

    # rows_still_null = rows_to_update.filter(postal_code_id_id__isnull=True)
    # if len(rows_still_null) > 0:
        # update_postalcodes_from_empty_resaletransactions_postalcodes(rows_still_null)

def update_postalcodes_from_empty_resaletransactions_postalcodes(rows_to_update) -> None:
    for row in rows_to_update:
        block:str = row.block
        street_name:str = row.street_name
        try:
            postalcode_object = PostalCodeAddress.objects.get(block=block, street_name=street_name)
            row.postal_code_id_id = postalcode_object.id
            print(f"postal code id for {block} {street_name} exists as {postalcode_object.id}")
        except ObjectDoesNotExist as e:
            print(f"postal code for {block} {street_name} does not exist. attempting to save...")
            try:
                postalcode_object:PostalCodeAddress = create_postalcode_object(block=block, street_name=street_name)
                postalcode_object.save()
                row.postal_code_id_id = postalcode_object.id
                print(f"postal code id for {block} {street_name} is now ({postalcode_object.id})")
            except (AttributeError, ValidationError) as e:
                print(f"Error creating '{block} {street_name}' postalcodeaddress object: {e}")
                continue
            except Exception as e:
                print(f"Uncaught error for '{block} {street_name}' in being registered as new address: {e}")
                continue
        except Exception as e:
            print(f"Uncaught error for getting postal code data: {e}")
            continue
    ResaleTransaction.objects.bulk_update(rows_to_update, ['postal_code_id_id'], batch_size=50000)

def import_from_csv_to_db(table_name, folderpath):
    conn = psycopg2.connect(host=env("DB_HOST"),dbname = env("DB_NAME"), user=env("DB_USER"), password=env("DB_PASSWORD"), port=env("DB_PORT"))

    cur = conn.cursor()

    # create temperary table with schema of real table
    cur.execute(f"""--sql 
                CREATE TEMPORARY TABLE tmp_table AS SELECT * FROM {table_name} WITH NO DATA;
                """)

    # find latest file in folderpath
    filepath:str|None = get_latest_file_in_folder(folderpath, "with-id", "csv")
    if filepath ==  None:
        cur.close()
        conn.close()
        return

    # copy csv items to temp table. csv file must have id column as primary key
    with open(filepath) as f:
        cur.copy_expert("COPY tmp_table FROM STDIN WITH HEADER CSV DELIMITER as ','", f)
        
    # cur.execute(f"SELECT * FROM tmp_table;")
    # for row in cur.fetchall():
    #     print(row)

    # add new stuff from temp table to real table
    cur.execute(f"""--sql
                INSERT INTO {table_name}
                SELECT * FROM tmp_table
                ON CONFLICT DO NOTHING;
                """)

    # cur.execute(f"SELECT * FROM {table_name};")
    # for row in cur.fetchall():
    #     print(row)

    # delete temp table
    cur.execute("""--sql
                DROP TABLE tmp_table;
                """)

    conn.commit()
    cur.close()
    conn.close()
