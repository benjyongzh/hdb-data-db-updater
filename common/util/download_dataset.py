from resale_transactions.resale_transaction_service import META_URL
import requests
from requests.exceptions import HTTPError
import re
from typing import Dict, List


def get_download_url(dataset_id) -> str:
    """
        Fetch dataset from data.gov.sg API using the datastore_search endpoint.
        If a download URL is returned, fetch the actual dataset and save to file.
        """

    meta_url = f"https://api-open.data.gov.sg/v1/public/api/datasets/{dataset_id}/initiate-download"

    r = requests.get(meta_url, timeout=30)
    r.raise_for_status()
    j = r.json()
    url = j.get("data", {}).get("url")
    if not url:
        raise RuntimeError("No download URL in API response")
    return url


def download_bytes(download_url: str) -> bytes:
    r = requests.get(download_url, timeout=60)
    r.raise_for_status()
    return r.content  # CSV bytes


def parse_description(desc_html: str) -> Dict[str, str]:
    """
    Extracts <th>label</th> <td>value</td> pairs from the HTML snippet
    commonly found under GeoJSON feature properties["Description"].
    Returns a dict of label->value, including an underscore version of the key.
    """
    pairs = re.findall(r"<th>\s*([^<]+?)\s*</th>\s*<td>\s*([^<]+?)\s*</td>", desc_html or "", flags=re.IGNORECASE)
    d: Dict[str, str] = {}
    for k, v in pairs:
        key = k.strip()
        val = v.strip()
        d[key] = val
        d[key.replace(" ", "_")] = val
    return d


def strip_z_polygon_coords(coords: List[List[List[float]]]) -> List[List[List[float]]]:
    """Drop the Z component from Polygon coordinates array."""
    return [[ [pt[0], pt[1]] for pt in ring ] for ring in coords]


def strip_z_multipolygon_coords(coords: List[List[List[List[float]]]]) -> List[List[List[List[float]]]]:
    """Drop the Z component from MultiPolygon coordinates array."""
    return [ strip_z_polygon_coords(poly) for poly in coords ]
