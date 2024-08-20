
import psycopg2
from common.util.get_latest_file_in_folder import get_latest_file_in_folder
from config.env import env
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import types

def update_resaletransactions_table_with_csv(table_name,csv_file) -> None:
    # pandas dataframe of file
    dataframe = pd.read_csv(csv_file)
    dataframe['postal_code_id_id'] = None

    # get db connection
    db_connection_url = f"postgresql://{env('DB_USER')}:{env('DB_PASSWORD')}@{env('DB_HOST')}:{env('DB_PORT')}/{env('DB_NAME')}"
    engine = create_engine(db_connection_url)

    # use csv to update entire table
    dataframe.to_sql(table_name, engine, if_exists='replace', index=False, chunksize=50000,
                     dtype={
                         'month': types.VARCHAR(7), 
                        'town': types.VARCHAR(100),
                        'flat_type': types.VARCHAR(50),
                        'block': types.VARCHAR(4),
                        'street_name': types.VARCHAR(100),
                        'storey_range': types.VARCHAR(10),
                        'floor_area_sqm': types.DECIMAL(7,2),
                        'flat_model': types.VARCHAR(50),
                        'lease_commence_date': types.VARCHAR(4),
                        'remaining_lease': types.VARCHAR(100),
                        'resale_price': types.DECIMAL(12,2),
                        'postal_code_id_id': types.BigInteger(),
                        })


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
