import psycopg2
from dotenv import dotenv_values

config = dotenv_values(".env")

conn = psycopg2.connect(host=config["HOST"],dbname = config["DBNAME"], user=config["USER"], password=config["PASSWORD"], port=config["DB_PORT"])

cur = conn.cursor()

#do stuff
cur.execute("""--sql SELECT * FROM practice;""")
for row in cur.fetchall():
    print(row)

cur.execute("""--sql CREATE TEMP TABLE tmp_table AS SELECT * FROM practice WITH NO DATA;""")

cur.execute("""--sql COPY tmp_table FROM '<file-here>.csv' DELIMITER ',' CSV;""")
            
cur.execute("""--sql INSERT INTO practice SELECT * FROM tmp_table ON CONFLICT DO NOTHING;""")

cur.execute("""--sql DROP TABLE tmp_table;""")

conn.commit()

cur.close()
conn.close()