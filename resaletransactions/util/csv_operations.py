
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


def update_resaletransactions_table_with_csv(table_name,csv_file,column_to_add:str) -> None:
    # pandas dataframe of file
    dataframe = pd.read_csv(csv_file)
    
    dataframe[column_to_add] = None

    # get db connection
    db_connection_url = f"postgresql://{env('DB_USER')}:{env('DB_PASSWORD')}@{env('DB_HOST')}:{env('DB_PORT')}/{env('DB_NAME')}"
    engine = create_engine(db_connection_url)

    with engine.connect() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table_name};"))

    # use csv to update entire table
    dataframe.to_sql(table_name, engine, if_exists='append', index=False, chunksize=50000,
                    #  dtype={
                    #      'month': types.VARCHAR(7), 
                    #     'town': types.VARCHAR(100),
                    #     'flat_type': types.VARCHAR(50),
                    #     'block': types.VARCHAR(4),
                    #     'street_name': types.VARCHAR(100),
                    #     'storey_range': types.VARCHAR(10),
                    #     'floor_area_sqm': types.DECIMAL(7,2),
                    #     'flat_model': types.VARCHAR(50),
                    #     'lease_commence_date': types.VARCHAR(4),
                    #     'remaining_lease': types.VARCHAR(100),
                    #     'resale_price': types.DECIMAL(12,2),
                    #     'postal_code_id_id': types.BigInteger(),
                    #     }
                        )

def set_primary_key(engine, table_name:str, pk_column_name: str):
    with engine.connect() as conn:
        conn.execute(f"ALTER TABLE {table_name} ADD PRIMARY KEY({pk_column_name});")

def set_foreign_key(engine, table_name:str, fk_column_name:str, fk_ref_table_name:str, fk_ref_col_name:str):
    with engine.connect() as conn:
        conn.execute(f"ALTER TABLE {table_name} ADD FOREIGN KEY({fk_column_name}) REFERENCES {fk_ref_table_name}({fk_ref_col_name});")   

def get_postal_code_ids(dataframe) -> List[int]:
    final_array:List[int] = []
    for i in range(len(dataframe.index)):
        block:str = dataframe.at[i, 'block']
        street_name:str = dataframe.at[i, 'street_name']
        print(f"row {i}, setting postal code key for {block} {street_name}...")
        postalcode_id:int|None = None
        try:
            postalcode_object = PostalCodeAddress.objects.get(block=block, street_name=street_name)
            postalcode_id = getattr(postalcode_object, "id")
            # dataframe.at[i, 'postal_code_id_id'] = postalcode
        except ObjectDoesNotExist as e:
            print(f"postal code for {block} {street_name} does not exist. attempting to save...")
            try:
                postalcode_object:PostalCodeAddress = create_postalcode_object(block=block, street_name=street_name)
                PostalCodeAddress.objects.create(postalcode_object)
                postalcode_id = getattr(postalcode_object, "id")
                print(f"postal code id for {block} {street_name} is now {postalcode_id}")
            except (AttributeError, ValidationError) as e:
                print(f"Error creating '{block} {street_name}' postalcodeaddress object: {e}")
                continue
            except Exception as e:
                print(f"Uncaught error for '{block} {street_name}' in being registered as new address: {e}")
                continue
        except Exception as e:
            print(f"Uncaught error for getting postal code data: {e}")
            continue
        final_array.append(postalcode_id)
    return final_array

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
