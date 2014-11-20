import os
import sys

from urlparse import urljoin

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')

sys.path.append(vendor_dir)
import requests


class Api(object):
    ENDPOINT = 'http://api.gbif.org/v1/'
    OCCURRENCES_SEARCH_URL = urljoin(ENDPOINT, "occurrence/search")

    def get_occurrences(self, filters, format):
        p = {'hasCoordinate': 'true', 'scientificName': 'tetraodon fluviatilis'}
        req = requests.get(self.OCCURRENCES_SEARCH_URL, params=p)
        resp = req.json()

        # TODO iterate over all results !!
        return resp['results']
