import requests
import urllib.parse
from ratelimit import limits, sleep_and_retry

# FIFTEEN_MINUTES = 900
@sleep_and_retry
@limits(calls=250, period=60)
def get_postal_code_from_address(address:str) -> str:
    encoded_address:str = urllib.parse.quote(address)
    try:
        response = requests.get(f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={encoded_address}&returnGeom=N&getAddrDetails=Y")
    # print(response.json())
        if int(response.json()['found']) > 0:
            postal_code = response.json()['results'][0]['POSTAL']
        else:
            postal_code = ""
        return postal_code
    except:
        # raise Exception('API response: {}'.format(response.status_code))
        raise Exception('Onemap API response error')
