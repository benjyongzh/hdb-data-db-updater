import psycopg2
from dotenv import dotenv_values

config = dotenv_values(".env")

conn = psycopg2.connect(host=config["HOST"],dbname = config["DBNAME"], user=config["USER"], password=config["PASSWORD"], port=config["DB_PORT"])

cur = conn.cursor()

#do stuff
cur.execute("""SELECT * FROM practice;""")
for row in cur.fetchall():
    print(row)

conn.commit()

cur.close()
conn.close()