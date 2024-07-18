import requests
import urllib.parse

def get_postal_code_from_address(address:str) -> str:
    encoded_address:str = urllib.parse.quote(address)
    response = requests.get(f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={encoded_address}&returnGeom=N&getAddrDetails=Y")
    # print(response.json())
    postal_code = response.json()['results'][0]['POSTAL']
    return postal_code

# get_postal_code_from_address("467 ADMIRALTY DR")