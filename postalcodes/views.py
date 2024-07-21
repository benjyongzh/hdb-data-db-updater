from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from resaletransactions.models import ResaleTransaction
from .models import PostalCodeAddress
from .util.get_postal_code_from_address import get_postal_code_from_address

@api_view(['GET'])
def refresh_postal_code_data(request):
    all_addresses = ResaleTransaction.objects.distinct("block", "street_name").values("block", "street_name")
    recorded_addresses = PostalCodeAddress.objects.all().values("block", "street_name")

    # see what addresses are missing in postalcodeaddress table.
    new_addresses = all_addresses.difference(recorded_addresses).order_by("street_name")

    # for each row missing in table, call openmaps api to get postal code of address.
    new_postal_code_objects = []
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
    data = {"redirect_url": "/postal-codes/", "new_addresses": final_new_addresses}
    return Response(data, status= status.HTTP_201_CREATED if len(final_new_addresses) > 0 else status.HTTP_200_OK)