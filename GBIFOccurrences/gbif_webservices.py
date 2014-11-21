import os
import sys

from urlparse import urljoin

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')

sys.path.append(vendor_dir)
import requests

ENDPOINT = 'http://api.gbif.org/v1/'
OCCURRENCES_SEARCH_URL = urljoin(ENDPOINT, "occurrence/search")
RECORDS_PER_PAGE = 300  # Maximum currently supported by API


def get_all_occurrences(filters):
    fixed_filters = {'hasCoordinate': 'true', 'limit': RECORDS_PER_PAGE}
    p = dict(filters.items() + fixed_filters.items())

    results = []
    offset = 0
    while True:
        p['offset'] = offset

        req = requests.get(OCCURRENCES_SEARCH_URL, params=p)

        resp = req.json()
        [results.append(r) for r in resp['results']]

        if resp['endOfRecords']:
            break

        offset = offset + RECORDS_PER_PAGE
    
    # TODO iterate over all results !!
    return results
