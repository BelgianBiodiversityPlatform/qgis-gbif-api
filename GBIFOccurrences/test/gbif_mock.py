import os

from httmock import all_requests, response

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


def _sample_data(path):
    p = os.path.join(__location__, 'sample_gbif_data', path)
    return open(p, 'r').read()


@all_requests
def gbif_v1_response(url, request):
    headers = {'content-type': 'application/json'}
    
    if url.query == 'limit=300&offset=0&scientificName=Tetraodon+fluviatilis&hasCoordinate=true':
        content = _sample_data('all_t_fluviatilis.json')
    elif url.query == 'limit=300&offset=0&scientificName=inexisting&hasCoordinate=true':
        content = _sample_data('no_results.json')

    return response(200, content, headers)
