import geojson

def get_postal_code_from_feature(feature) -> str:
    # feature = collection['features'][0]
    description = feature['properties']['Description']
    # postal_code = feature['properties']['geometry']
    geometry = feature['geometry']
    return description


filepath = "/home/benjyongzh/hdb-info/building-polygons/HDBExistingBuilding-sample-unformatted.geojson"
with open(filepath) as f:
    gj = geojson.load(f)
    print(get_postal_code_from_feature(gj['features'][0]))