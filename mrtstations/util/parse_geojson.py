from django.contrib.gis.geos import Polygon
from django.db import connection
from mrtstations.models import MrtStation
import json
from bs4 import BeautifulSoup
from common.util.utils import remove_z_from_geom_coordinates
from mrtstations.static_data import STATIONS
from mrtstations.models import Line

def import_new_geojson_features_into_table(
    model_object,
    geojson_file,
    progress_record={
        'progress_recorder': None,
        'steps_remaining': 0
    }):

    try:
        gj = json.load(geojson_file)
    except (FileNotFoundError) as e:
        raise Exception(f"Error: {e}")

    # # iterate through every feature
    features = gj['features']

    polygons = []

    progress_recorder = progress_record['progress_recorder']
    steps_remaining = progress_record['steps_remaining']

    # for each feature, get postalcode
    for feature_index,feature in enumerate(features):
        try:

            original_description = feature['properties']['Description']
            station_info = parse_description(original_description)
            name=station_info["NAME"]
            rail_type=station_info["RAIL_TYPE"]
            ground_level=station_info["GRND_LEVEL"]

        except(ValueError, KeyError) as e:
            print(f"Key-value Error for feature {feature_index}: {e}")
            continue

        db_row = model_object.objects.filter(name__exact=name).first()
        # if postalcode doesnt exist in db
        if db_row != None:
            continue

        # get geometry object,
        geom = feature['geometry']

        # remove z axis from geometry, use first index of coordinates only
        try:
            geom_coordinates = remove_z_from_geom_coordinates(geom['coordinates'])
            final_geom = Polygon(geom_coordinates)
        except (SyntaxError, ValueError, IndexError) as e:
            print(f"""
                    Error for feature {feature_index} ({name} MRT station) in making Polygon object:
                    {e}
                    Original coordinates:
                    {geom['coordinates']}
                    Refined coordinates:
                    {geom_coordinates}
                """)
            continue

        polygons.append(model_object(
                name=name,
                rail_type = rail_type,#MRT or LRT
                ground_level = ground_level,#ABOVEGROUND or UNDERGROUND
                building_polygon = final_geom
            ))
        
        
        if progress_recorder != None:
            progress_recorder.set_progress(feature_index, len(features) + steps_remaining, description=f"Inserting Geojson item {feature_index} out of {len(features)}")
        
    model_object.objects.bulk_create(polygons)

    # TODO add_line_relationship here? add in progress recorder as a dependency to update too. check total length of progress
    # add_line_relationship(model_object, Line, STATIONS)

    return features

def parse_description(string):
    rows = BeautifulSoup(string, "lxml")("tr")
    content = {}
    for row in rows[1:]:
        header = str(row("th")).split("&lt;")[0].split("[<th>")[1].split("</th>]")[0]
        data = str(row("td")).split("&lt;")[0].split("[<td>")[1].split("</td>]")[0]
        content[header]= data
    return content

def merge_polygons(table_name, name_col, geometry_col, rail_type_col, ground_level_col):
    """
    Merges overlapping polygons for entries with the same name while retaining attributes.
    
    Args:
        table_name (str): The name of the database table.
        name_col (str): The name of the column storing station names.
        geometry_col (str): The name of the geometry column.
        rail_type_col (str): The name of the column storing rail type ("MRT"/"LRT").
        ground_level_col (str): The name of the column storing ground level ("UNDERGROUND"/"ABOVEGROUND").
    """
    with connection.cursor() as cursor:
        # Step 1: Identify duplicate names
        duplicate_names_query = """
            SELECT {name_col}
            FROM {table_name}
            GROUP BY {name_col}
            HAVING COUNT(*) > 1
        """.format(table_name=table_name, name_col=name_col)
        cursor.execute(duplicate_names_query)
        duplicate_names = cursor.fetchall()

        for name_tuple in duplicate_names:
            name = name_tuple[0]

            # Step 2: Fetch rail_type and ground_level (assuming consistency)
            fetch_attributes_query = """
                SELECT {rail_type_col}, {ground_level_col}
                FROM {table_name}
                WHERE {name_col} = %s
                LIMIT 1
            """.format(table_name=table_name, name_col=name_col, rail_type_col=rail_type_col, ground_level_col=ground_level_col)
            cursor.execute(fetch_attributes_query, [name])
            rail_type, ground_level = cursor.fetchone()

            # Step 3: Merge geometries for this name
            merge_geometries_query = """
                SELECT ST_Union({geometry_col})
                FROM {table_name}
                WHERE {name_col} = %s
            """.format(table_name=table_name, name_col=name_col, geometry_col=geometry_col)
            cursor.execute(merge_geometries_query, [name])
            merged_geometry = cursor.fetchone()[0]

            # Step 4: Count distinct polygons to handle non-overlapping cases
            distinct_geometry_query = """
                SELECT COUNT(DISTINCT {geometry_col})
                FROM (
                    SELECT (ST_Dump({geometry_col})).geom AS {geometry_col}
                    FROM {table_name}
                    WHERE {name_col} = %s
                ) AS dumped
            """.format(table_name=table_name, name_col=name_col, geometry_col=geometry_col)
            cursor.execute(distinct_geometry_query, [name])
            distinct_geometry_count = cursor.fetchone()[0]

            # Step 5: Insert merged or original geometries and remove old rows
            delete_original_query = """
                DELETE FROM {table_name} WHERE {name_col} = %s
            """.format(table_name=table_name, name_col=name_col)
            cursor.execute(delete_original_query, [name])

            if distinct_geometry_count == 1:
                # All polygons merged into one
                insert_merged_query = """
                    INSERT INTO {table_name} ({name_col}, {geometry_col}, {rail_type_col}, {ground_level_col})
                    VALUES (%s, %s, %s, %s)
                """.format(table_name=table_name, name_col=name_col, geometry_col=geometry_col, 
                           rail_type_col=rail_type_col, ground_level_col=ground_level_col)
                cursor.execute(insert_merged_query, [name, merged_geometry, rail_type, ground_level])
            else:
                # Polygons are distinct, keep them separate
                fetch_geometries_query = """
                    SELECT {geometry_col}
                    FROM {table_name}
                    WHERE {name_col} = %s
                """.format(table_name=table_name, name_col=name_col, geometry_col=geometry_col)
                cursor.execute(fetch_geometries_query, [name])
                geometries = cursor.fetchall()

                for geometry in geometries:
                    insert_distinct_query = """
                        INSERT INTO {table_name} ({name_col}, {geometry_col}, {rail_type_col}, {ground_level_col})
                        VALUES (%s, %s, %s, %s)
                    """.format(table_name=table_name, name_col=name_col, geometry_col=geometry_col, 
                               rail_type_col=rail_type_col, ground_level_col=ground_level_col)
                    cursor.execute(insert_distinct_query, [name, geometry[0], rail_type, ground_level])

        print("Polygons merged successfully with attributes!")

def add_line_relationship(model_a, model_b, static_data):
    # model_a is stations
    # model b is lines
    for key, value in static_data.items():
        stations = model_a.objects.filter(name__contains=key)
        if not stations:
            print(f"{key} station not found in mrtstations database")
            continue
        lines = model_b.objects.filter(abbreviation__in=value)
        if not lines:
            print(f"{key}'s lines not found in lines database")
            continue
        stations.lines.add(lines)