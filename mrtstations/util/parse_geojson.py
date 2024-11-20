from django.contrib.gis.geos import Polygon, GEOSGeometry
import json
from bs4 import BeautifulSoup
from common.util.utils import remove_z_from_geom_coordinates
from django.db.models import Count

def import_new_geojson_features_into_table(
    model_object,
    geojson_file,
    progress_record={
        'progress_recorder': None,
        'total_big_steps': 0
    }):

    try:
        gj = json.load(geojson_file)
    except (FileNotFoundError) as e:
        raise Exception(f"Error: {e}")

    # # iterate through every feature
    features = gj['features']

    polygons = []

    progress_recorder = progress_record['progress_recorder']

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
            progress_recorder.set_progress(feature_index, len(features), description=f"Step 1 out of {progress_record['total_big_steps']}: Inserting Geojson item {feature_index} out of {len(features)}")
        
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

def merge_polygons_with_intersection_logic(model_object, progress_record={
        'progress_recorder': None,
        'total_big_steps': 0
    }):
    """
    Merges intersecting polygons where name and rail_type are identical.
    If ground_level differs, resulting ground_level is set to 'BOTH'.
    Non-intersecting polygons are retained as separate rows.
    """

    
    # Step 1: Identify groups by name and rail_type
    groups = (
        model_object.objects
        .values("name", "rail_type")
        .annotate(count=Count("id"))
        .filter(count__gt=1)
    )

    for index, group in enumerate(groups):
        name = group["name"]
        rail_type = group["rail_type"]

        # Step 2: Retrieve all rows for this group
        rows = list(
            model_object.objects.filter(name=name, rail_type=rail_type)
        )

        processed_geometries = []
        new_rows = []

        # Step 3: Check and merge intersecting polygons
        for row in rows:
            geom = GEOSGeometry(row.building_polygon)
            found_intersection = False

            for processed in processed_geometries:
                if geom.intersects(processed["building_polygon"]):
                    # Merge geometries
                    processed["building_polygon"] = processed["building_polygon"].union(geom)
                    # Update ground_level to 'BOTH' if needed
                    if processed["ground_level"] != row.ground_level:
                        processed["ground_level"] = "BOTH"
                    found_intersection = True
                    break

            if not found_intersection:
                # Add as a new processed geometry
                processed_geometries.append({
                    "building_polygon": geom,
                    "ground_level": row.ground_level,
                })

        # Step 4: Prepare rows for insertion
        for processed in processed_geometries:
            new_rows.append(model_object(
                name=name,
                rail_type=rail_type,
                ground_level=processed["ground_level"],
                building_polygon=processed["building_polygon"]
            ))

        # Step 5: Delete old rows and insert new ones
        model_object.objects.filter(name=name, rail_type=rail_type).delete()
        model_object.objects.bulk_create(new_rows)
        
        if progress_record['progress_recorder'] != None:
            progress_record['progress_recorder'].set_progress(index, len(groups), description=f"Step 2 out of {progress_record['total_big_steps']}: Merging polygons of {name} station, if possible")

    print("Polygons merged successfully based on intersection logic!")

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