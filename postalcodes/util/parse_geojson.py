import geojson
from bs4 import BeautifulSoup

def get_postal_code_from_feature(feature) -> str:
    description = feature['properties']['Description']
    postal_code:str = get_postal_code_from_description(description)
    # geometry = feature['geometry']
    return postal_code


def get_postal_code_from_description(description) -> str:
    table_data = [[cell.text for cell in row("td")]
        for row in BeautifulSoup(description, features="html.parser")("tr")]
    return table_data[4][0]

def get_geometry_from_feature(feature):
    return feature['geometry']

filepath = "/home/benjyongzh/hdb-info/building-polygons/HDBExistingBuilding-sample-unformatted.geojson"
with open(filepath) as f:
    gj = geojson.load(f)
    print(get_postal_code_from_feature(gj['features'][0]))