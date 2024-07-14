from django.http import HttpResponse
import psycopg2
from dotenv import dotenv_values
from django.shortcuts import redirect

config = dotenv_values(".env")
conn = psycopg2.connect(host=config["DB_HOST"],dbname = config["DB_NAME"], user=config["DB_USER"], password=config["DB_PASSWORD"], port=config["DB_PORT"])
    
#! need to choose csv file to copy from
def import_from_csv(table_name, filepath):
    cur = conn.cursor()
    #do stuff
    cur.execute(f"""--sql 
                CREATE TEMPORARY TABLE tmp_table AS SELECT * FROM {table_name} WITH NO DATA;
                """)
    # cur.execute("""--sql
    #             CREATE TEMPORARY TABLE tmp_table AS SELECT * FROM datacollector_resaletransaction WITH NO DATA;
    #             """)

    with open(filepath) as f:
        cur.copy_expert('COPY tmp_table FROM STDIN WITH HEADER CSV', f)

    #! csv doesnt have id as bigInt. have to omit id somehow. use EXCEPT?
    cur.execute(f"""--sql
                INSERT INTO {table_name} SELECT * FROM tmp_table ON CONFLICT DO NOTHING;
                """)
    # cur.execute("""--sql
    #             INSERT INTO datacollector_resaletransaction SELECT * FROM tmp_table ON CONFLICT DO NOTHING;
    #             """)

    cur.execute(f"SELECT * FROM {table_name};")
    # cur.execute("""SELECT * FROM datacollector_resaletransaction;""")
    for row in cur.fetchall():
        print(row)

    cur.execute("""--sql
                DROP TABLE tmp_table;
                """)

    conn.commit()
    cur.close()
    conn.close()

# Create your views here.
def update_resale_prices(request):
    import_from_csv("datacollector_resaletransaction", config["CSV_FILE_PATH"])
    # return HttpResponse("update resale prices here")
    return redirect('data/resaleprices')

def update_building_polygons(request):
    return HttpResponse("update building polygons here")