import psycopg2
from dotenv import dotenv_values

config = dotenv_values(".env")

conn = psycopg2.connect(host=config["DB_HOST"],dbname = config["DB_NAME"], user=config["DB_USER"], password=config["DB_PASSWORD"], port=config["DB_PORT"])

cur = conn.cursor()

#do stuff

cur.execute("""--sql
            CREATE TEMPORARY TABLE tmp_table AS SELECT * FROM practice WITH NO DATA;
            """)

with open(config["CSV_FILE_PATH"]) as f:
    cur.copy_expert('COPY tmp_table FROM STDIN WITH HEADER CSV', f)

cur.execute("""--sql
            INSERT INTO practice SELECT * FROM tmp_table ON CONFLICT DO NOTHING;
            """)

cur.execute("""SELECT * FROM practice;""")
for row in cur.fetchall():
    print(row)

cur.execute("""--sql
            DROP TABLE tmp_table;
            """)

conn.commit()

cur.close()
conn.close()

# do same gathering of data for building-polygons

# execute merging of tables with building-polygons. save as 3rd table. subprocess in python

# learn djnago as backend