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


def _finalize_filters(filters):
    fixed_filters = {'hasCoordinate': 'true', 'limit': RECORDS_PER_PAGE}
    return dict(filters.items() + fixed_filters.items())


def get_occurrences_in_baches(filters):
    p = _finalize_filters(filters)

    finished = False
    offset = 0
    current_count = 0
    while not finished:
        p['offset'] = offset
        req = requests.get(OCCURRENCES_SEARCH_URL, params=p)

        resp = req.json()

        if resp['endOfRecords']:
            finished = True  # This will be the last turn...

        # We only retrieve this value once...
        if offset == 0:
            total_count = resp['count']

        if finished:
            current_count = total_count
        else:
            current_count = current_count + RECORDS_PER_PAGE
        percentage_done = ((current_count / float(total_count)) * 100)
        
        yield (resp['results'], percentage_done)

        offset = offset + RECORDS_PER_PAGE
