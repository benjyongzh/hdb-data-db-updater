import geojson
from bs4 import BeautifulSoup

def get_postal_code_from_feature(feature) -> str:
    description = feature['properties']['Description']
    postal_code:str = get_postal_code_from_description(description)
    return postal_code

def get_postal_code_from_description(description) -> str:
    table_data = [[cell.text for cell in row("td")]
        for row in BeautifulSoup(description, features="html.parser")("tr")]
    return table_data[4][0]

def get_block_number_from_feature(feature) -> str:
    description = feature['properties']['Description']
    block:str = get_block_number_from_description(description)
    return block

def get_block_number_from_description(description) -> str:
    table_data = [[cell.text for cell in row("td")]
        for row in BeautifulSoup(description, features="html.parser")("tr")]
    return table_data[1][0]

def get_geometry_from_feature(feature):
    return feature['geometry']

filepath = "/home/benjyongzh/hdb-info/building-polygons/HDBExistingBuilding-sample-unformatted.geojson"
with open(filepath) as f:
    gj = geojson.load(f)
    print(get_block_number_from_feature(gj['features'][0]))

# def import_new_geojson_features_into_postgis(file):
    # iterate through every feature
    # for each feature, get postalcode
    # if postalcode doesnt exist in db, get geometry and create new row with postalcode + geometry. use 