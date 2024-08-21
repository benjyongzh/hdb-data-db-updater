
from resaletransactions.models import ResaleTransaction
from postalcodes.models import PostalCodeAddress
import requests
import urllib.parse
from ratelimit import limits, sleep_and_retry
from api.serializers import PostalCodeAddressSerializer

def update_postalcode_address_table() -> None:
    all_addresses = ResaleTransaction.objects.distinct("block", "street_name").values("block", "street_name")
    recorded_addresses = PostalCodeAddress.objects.all().values("block", "street_name")

    # see what addresses are missing in postalcodeaddress table.
    new_addresses = all_addresses.difference(recorded_addresses).order_by("street_name")

    # for each row missing in table, call openmaps api to get postal code of address.
    new_postal_code_objects:list[PostalCodeAddress] = []
    for address_index,address_info in enumerate(new_addresses):
        address_string = f"{address_info['block']} {address_info['street_name']}"
        try:
            address_with_postal_code:PostalCodeAddress = create_postalcode_object(block=address_info['block'], street_name=address_info['street_name'])
            new_postal_code_objects.append(address_with_postal_code)
        except Exception as e:
            print(f"Error for '{address_string}' in being registered as new address: {e}")
            continue

    # add address and postal code as new row to postalcodeaddress table.
    try:
        final_new_addresses = PostalCodeAddress.objects.bulk_create(new_postal_code_objects)
    except Exception as e:
        raise f"Failed to create new postalcodeaddresses: {e}"
    #! for each row extra in table, delete row.
    
    # respond with new addresses
    serializer = PostalCodeAddressSerializer(final_new_addresses, many=True)
    return serializer.data

# FIFTEEN_MINUTES = 900
@sleep_and_retry
@limits(calls=250, period=60)
def get_postal_code_from_address(address:str) -> str:
    encoded_address:str = urllib.parse.quote(address)
    try:
        response = requests.get(f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={encoded_address}&returnGeom=N&getAddrDetails=Y")
        return response.json()['results'][0]['POSTAL']
    except (KeyError, ValueError, IndexError) as e:
        print(f"""
                Error for address {address}:
                {e}
                Response received:
                {response.json()}
            """)
        return ""
    
    except Exception as e:
        print(f"""
                Unexpected error for address {address}:
                {e}
            """)
        return ""

def create_postalcode_object(block:str, street_name:str) -> PostalCodeAddress:
    address_string = f"{block} {street_name}"
    print(f"Attempting to create postal code for: '{address_string}'")
    postal_code:str = get_postal_code_from_address(address_string)
    
    return PostalCodeAddress(
        block = block,
        street_name = street_name,
        postal_code = postal_code)
    