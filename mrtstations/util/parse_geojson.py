from django.contrib.gis.geos import Polygon
import json
from bs4 import BeautifulSoup
from common.util.utils import remove_z_from_geom_coordinates

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

        # create new row with block + postalcode + geometry,
        # use SELECT ST_GeomFromGeoJSON to convert from geojson to postGIS geom,
        # ST_AsText,
        # ST_AsGeoJSON to convert from postGIS geom to geojson
        # new_polygon = {
        #     "block": block_number,
        #     "postal_code": postal_code,
        #     "building_polygon": final_geom
        # }

        polygons.append(model_object(
                name=name,
                rail_type = rail_type,#MRT or LRT
                ground_level = ground_level,#ABOVEGROUND or UNDERGROUND
                building_polygon = final_geom
            ))
        
        if progress_recorder != None:
            progress_recorder.set_progress(feature_index, len(features) + steps_remaining, description=f"Inserting Geojson item {feature_index} out of {len(features)}")
        
    model_object.objects.bulk_create(polygons)

    return features

def parse_description(string):
    rows = BeautifulSoup(string, "lxml")("tr")
    content = {}
    for row in rows[1:]:
        header = str(row("th")).split("&lt;")[0].split("[<th>")[1].split("</th>]")[0]
        data = str(row("td")).split("&lt;")[0].split("[<td>")[1].split("</td>]")[0]
        content[header]= data
    return content