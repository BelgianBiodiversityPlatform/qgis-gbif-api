import os
import sys

from urllib.parse import urljoin

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.append(vendor_dir)
import requests

ENDPOINT = 'http://api.gbif.org/v1/'
OCCURRENCES_SEARCH_URL = urljoin(ENDPOINT, "occurrence/search")
RECORDS_PER_PAGE = 300  # Maximum currently supported by API
MAX_TOTAL_RECORDS_GBIF = 200000


class ConnectionIssue(Exception):
    pass

class GBIFApiError(Exception):
    pass

def _finalize_filters(filters):
    fixed_filters = {'hasCoordinate': 'true', 'limit': RECORDS_PER_PAGE}
    return dict(list(filters.items()) + list(fixed_filters.items()))


def count_occurrences(filters):
    p = _finalize_filters(filters)
    p['offset'] = 0
    try:
        req = requests.get(OCCURRENCES_SEARCH_URL, params=p)
    except requests.exceptions.ConnectionError:
        raise ConnectionIssue
    else:
        try:
            resp = req.json()
        except ValueError:  # When GBIF throws an error message, it's plain text (not JSON)
            raise GBIFApiError(req.text)

        try:
            c = resp['count']
        except KeyError:
            # No "count" field when no results
            if resp['endOfRecords'] and (len(resp['results']) == 0):
                c = 0
    return c


def get_occurrences_in_baches(filters):
    p = _finalize_filters(filters)

    finished = False
    offset = 0
    current_count = 0
    total_count = count_occurrences(filters)

    while not finished:
        p['offset'] = offset
        req = requests.get(OCCURRENCES_SEARCH_URL, params=p)

        resp = req.json()

        if resp['endOfRecords']:
            finished = True  # This will be the last turn...

        if finished:
            current_count = total_count
        else:
            current_count = current_count + RECORDS_PER_PAGE

        yield (resp['results'])

        offset = offset + RECORDS_PER_PAGE
