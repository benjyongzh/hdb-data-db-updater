from bs4 import BeautifulSoup
from postalcodes.models import BuildingGeometryPolygon
from django.contrib.gis.geos import Polygon
import json
from common.util.utils import remove_z_from_geom_coordinates

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
            block_number:str = get_block_number_from_feature(feature)
            postal_code:str = get_postal_code_from_feature(feature)
        except(ValueError, KeyError) as e:
            print(f"Error for feature {feature_index}: {e}")
            continue

        db_row = model_object.objects.filter(block__exact=block_number, postal_code__exact=postal_code).first()
        # if postalcode doesnt exist in db
        if db_row != None:
            continue

        # get geometry object,
        geom = get_geometry_from_feature(feature)

        # remove z axis from geometry, use first index of coordinates only
        try:
            geom_coordinates = remove_z_from_geom_coordinates(geom['coordinates'])
            final_geom = Polygon(geom_coordinates)
        except (SyntaxError, ValueError, IndexError) as e:
            print(f"""
                    Error for feature {feature_index} (block {block_number}, postal code {postal_code}) in making Polygon object:
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

        polygons.append(BuildingGeometryPolygon(
                block=block_number,
                postal_code=postal_code,
                building_polygon=final_geom
            ))
        
        if progress_recorder != None:
            progress_recorder.set_progress(feature_index, len(features) + steps_remaining, description=f"Inserting Geojson item {feature_index} out of {len(features)}")
        
    BuildingGeometryPolygon.objects.bulk_create(polygons)

    return features



'''
geom = {
        "type": "Polygon",
        "coordinates": [
          [
            [103.801697204792006, 1.44919018597124, 0.0],
            [103.801691666848996, 1.44918060687489, 0.0],
            [103.801714863513993, 1.44916702456497, 0.0],
            [103.801696048167003, 1.44913447716152, 0.0],
            [103.801685882216006, 1.44914042953939, 0.0],
            [103.801679214759005, 1.44912889609754, 0.0],
            [103.801654116639995, 1.44914359255622, 0.0],
            [103.801643453202004, 1.44912514700757, 0.0],
            [103.801640931709002, 1.44912662289336, 0.0],
            [103.801628072143998, 1.44910437808254, 0.0],
            [103.801694765025999, 1.4490653276992, 0.0],
            [103.801687175628004, 1.44905219894715, 0.0],
            [103.801734135079002, 1.44902470243359, 0.0],
            [103.801722139947003, 1.44900395164396, 0.0],
            [103.801747064633005, 1.44898935737511, 0.0],
            [103.801739761882004, 1.44897672421847, 0.0],
            [103.801749968270002, 1.44897074742308, 0.0],
            [103.801731564473002, 1.44893891266414, 0.0],
            [103.801707701043, 1.44895288565, 0.0],
            [103.801702007646, 1.44894303795551, 0.0],
            [103.801658252633004, 1.44896865795921, 0.0],
            [103.801660659026993, 1.44897281896967, 0.0],
            [103.801606497234005, 1.44900453242738, 0.0],
            [103.801604201364995, 1.44900056133476, 0.0],
            [103.801560405013007, 1.44902620484936, 0.0],
            [103.801565729992006, 1.44903541586706, 0.0],
            [103.801541587092998, 1.4490495516326, 0.0],
            [103.801560539020997, 1.4490823350781, 0.0],
            [103.801570694190005, 1.44907638903119, 0.0],
            [103.801577601565995, 1.44908833848396, 0.0],
            [103.801602315080999, 1.44907386811159, 0.0],
            [103.801613958866994, 1.44909401116458, 0.0],
            [103.801570698084006, 1.44911934177709, 0.0],
            [103.801542757671001, 1.44907100857823, 0.0],
            [103.801507711960994, 1.44909152899591, 0.0],
            [103.801528743201004, 1.44912791002918, 0.0],
            [103.801499613025996, 1.44914496681796, 0.0],
            [103.801506315525998, 1.44915656085317, 0.0],
            [103.801441362343994, 1.44919459294207, 0.0],
            [103.801415757789997, 1.4491822235992, 0.0],
            [103.801425856560002, 1.44916104987909, 0.0],
            [103.801451641731006, 1.44917350785202, 0.0],
            [103.801457606816996, 1.44916100239763, 0.0],
            [103.801468733215003, 1.44916637809197, 0.0],
            [103.801485137650005, 1.44913198718785, 0.0],
            [103.801459787398997, 1.44911973993816, 0.0],
            [103.801464303898001, 1.4491102704116, 0.0],
            [103.801418635527, 1.44908820781636, 0.0],
            [103.801416526449003, 1.44909263012411, 0.0],
            [103.801360046189998, 1.44906534286629, 0.0],
            [103.801362196604003, 1.44906083374028, 0.0],
            [103.801316915529, 1.4490389574474, 0.0],
            [103.801311988357, 1.4490492879219, 0.0],
            [103.801286973282998, 1.44903720255614, 0.0],
            [103.801270774632002, 1.44907116208032, 0.0],
            [103.801281240562005, 1.44907621852583, 0.0],
            [103.801274835148007, 1.44908964732864, 0.0],
            [103.801300679625001, 1.44910213333938, 0.0],
            [103.801290613204003, 1.44912323651903, 0.0],
            [103.801297167551994, 1.44912640278902, 0.0],
            [103.801288060865005, 1.44914549467782, 0.0],
            [103.801281068902, 1.44914211678051, 0.0],
            [103.801270712223996, 1.44916382949693, 0.0],
            [103.801245512937996, 1.44915165550045, 0.0],
            [103.801239332180003, 1.44916461313294, 0.0],
            [103.801228835697998, 1.44915954131262, 0.0],
            [103.801212253331002, 1.44919430752309, 0.0],
            [103.801237322321001, 1.44920641821264, 0.0],
            [103.801232677317003, 1.44921615633285, 0.0],
            [103.801277989846, 1.44923804800208, 0.0],
            [103.801279858092002, 1.44923413123025, 0.0],
            [103.801308875507004, 1.44924815018228, 0.0],
            [103.801347356516004, 1.44916747517228, 0.0],
            [103.801423220361997, 1.44920412648528, 0.0],
            [103.801419481175003, 1.44921196635969, 0.0],
            [103.801381679098995, 1.44919370401073, 0.0],
            [103.801371429358994, 1.44921519154263, 0.0],
            [103.801367599548001, 1.44921334206483, 0.0],
            [103.801365699851004, 1.44921732485483, 0.0],
            [103.801346317165994, 1.44920796079953, 0.0],
            [103.801340511136999, 1.44922013435445, 0.0],
            [103.801337809960998, 1.44921883022385, 0.0],
            [103.801320592265995, 1.44925492674485, 0.0],
            [103.801345559715998, 1.4492669895005, 0.0],
            [103.801343422781002, 1.44927146968704, 0.0],
            [103.801368834136994, 1.44928374587855, 0.0],
            [103.801374517954002, 1.44927183096979, 0.0],
            [103.801430774468997, 1.44929900970053, 0.0],
            [103.801425150859998, 1.44931079890375, 0.0],
            [103.801449864009996, 1.44932273866122, 0.0],
            [103.801452089009999, 1.44931807489003, 0.0],
            [103.801478196778007, 1.44933068751342, 0.0],
            [103.801493941621999, 1.44929767756308, 0.0],
            [103.801490816309993, 1.44929616813615, 0.0],
            [103.801497331356003, 1.44928250962595, 0.0],
            [103.801477859708996, 1.44927310216105, 0.0],
            [103.801479756711004, 1.44926912479711, 0.0],
            [103.801475759761999, 1.44926719392441, 0.0],
            [103.801485726433995, 1.4492462996505, 0.0],
            [103.801433978169001, 1.44922129959677, 0.0],
            [103.801435331500997, 1.44921846081884, 0.0],
            [103.801514782826004, 1.44917193967467, 0.0],
            [103.801525452551999, 1.44919039517198, 0.0],
            [103.801521657731001, 1.44919261623518, 0.0],
            [103.801534160558006, 1.44921424426562, 0.0],
            [103.801510039223999, 1.44922836827432, 0.0],
            [103.801516763289996, 1.44923999848434, 0.0],
            [103.801506072551007, 1.44924625833755, 0.0],
            [103.801525463885, 1.4492798014549, 0.0],
            [103.801550877417995, 1.44926492051202, 0.0],
            [103.801555603943996, 1.44927309783377, 0.0],
            [103.801599318526996, 1.44924750134517, 0.0],
            [103.801597149358003, 1.44924375091904, 0.0],
            [103.801651973429998, 1.44921164949912, 0.0],
            [103.801654141700993, 1.44921540082956, 0.0],
            [103.801697204792006, 1.44919018597124, 0.0]
          ]
        ]
      }

print(remove_z_from_geom_coordinates(geom))
'''