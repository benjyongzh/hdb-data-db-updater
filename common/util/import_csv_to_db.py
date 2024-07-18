
import psycopg2
from dotenv import dotenv_values
from . import get_latest_file_in_folder

config = dotenv_values(".env")

def import_from_csv_to_db(table_name, folderpath):
    conn = psycopg2.connect(host=config["DB_HOST"],dbname = config["DB_NAME"], user=config["DB_USER"], password=config["DB_PASSWORD"], port=config["DB_PORT"])

    cur = conn.cursor()
    # create temperary table with schema of real table
    cur.execute(f"""--sql 
                CREATE TEMPORARY TABLE tmp_table AS SELECT * FROM {table_name} WITH NO DATA;
                """)

    #find latest file in folderpath
    filepath = get_latest_file_in_folder(folderpath)

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

    cur.execute(f"SELECT * FROM {table_name};")
    for row in cur.fetchall():
        print(row)

    # delete temp table
    cur.execute("""--sql
                DROP TABLE tmp_table;
                """)

    conn.commit()
    cur.close()
    conn.close()