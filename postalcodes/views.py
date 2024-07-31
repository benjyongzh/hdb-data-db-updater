from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from resaletransactions.models import ResaleTransaction
from .models import PostalCodeAddress
from .util.get_postal_code_from_address import get_postal_code_from_address
from .util.parse_geojson import import_new_geojson_features_into_table
from api.serializers import PostalCodeAddressSerializer,BuildingGeometryPolygonSerializer

from config.env import env

@api_view(['GET'])
def update_postal_code_data(request):
    try:
        all_addresses = ResaleTransaction.objects.distinct("block", "street_name").values("block", "street_name")
        recorded_addresses = PostalCodeAddress.objects.all().values("block", "street_name")

        # see what addresses are missing in postalcodeaddress table.
        new_addresses = all_addresses.difference(recorded_addresses).order_by("street_name")

        # for each row missing in table, call openmaps api to get postal code of address.
        new_postal_code_objects:list[PostalCodeAddress] = []
        for address_info in new_addresses:
            address_string = f"{address_info['block']} {address_info['street_name']}"
            postal_code:str = get_postal_code_from_address(address_string)
            address_with_postal_code:PostalCodeAddress = PostalCodeAddress(
                block = address_info['block'],
                street_name = address_info['street_name'],
                postal_code = postal_code)
            new_postal_code_objects.append(address_with_postal_code)
            print(address_with_postal_code)

        # add address and postal code as new row to postalcodeaddress table.
        final_new_addresses = PostalCodeAddress.objects.bulk_create(new_postal_code_objects)
        #! for each row extra in table, delete row.
        # respond with new addresses
        serializer = PostalCodeAddressSerializer(final_new_addresses, many=True)
        data = {"redirect_url": "/api/postal-codes/", "new_addresses": serializer.data}
        return Response(data, status= status.HTTP_201_CREATED if len(final_new_addresses) > 0 else status.HTTP_200_OK)
    except:
        data = {"error-message": "Invalid configurations"}
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def update_new_building_polygons(request):
    try:
        new_geojson = import_new_geojson_features_into_table("postalcodes_buildinggeometrypolygon", env("BUILDING_POLYGON_GEOJSON_FOLDER_PATH"))
    except:
        # respond with not ok. wrong config
        data = {"error-message": "Invalid configurations"}
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # respond with ok
    serializer = BuildingGeometryPolygonSerializer(new_geojson, many=True)
    data = {"redirect_url": "/api/postal-codes/", "new_polygons": serializer.data}
    return Response(data, status= status.HTTP_201_CREATED if len(new_geojson) > 0 else status.HTTP_200_OK)