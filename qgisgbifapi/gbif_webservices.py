from urllib.parse import urljoin
from qgis.PyQt.QtWidgets import QMessageBox
import requests

ENDPOINT = "http://api.gbif.org/v1/"
OCCURRENCES_SEARCH_URL = urljoin(ENDPOINT, "occurrence/search")
RECORDS_PER_PAGE = 300  # Maximum currently supported by API
MAX_TOTAL_RECORDS_GBIF = 200000
WARNING_THRESHOLD = 5000  # Threshold for showing the warning


class ConnectionIssue(Exception):
    pass


class GBIFApiError(Exception):
    pass


def _finalize_filters(filters):
    fixed_filters = {"hasCoordinate": "true", "limit": RECORDS_PER_PAGE}
    return dict(list(filters.items()) + list(fixed_filters.items()))


def show_warning():
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setText(
        f"The number of results is very large (> {WARNING_THRESHOLD}). Do you want to continue?"
    )
    msg_box.setWindowTitle("Warning")
    msg_box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    return msg_box.exec() == QMessageBox.StandardButton.Yes


def count_occurrences(filters):
    p = _finalize_filters(filters)
    p["offset"] = 0
    headers = {
        'User-Agent': 'QGIS Plugin GBIF Occurrences',
        'From': 'https://github.com/BelgianBiodiversityPlatform/qgis-gbif-api'
    }
    try:
        req = requests.get(OCCURRENCES_SEARCH_URL, params=p, headers=headers)
    except requests.exceptions.ConnectionError:
        raise ConnectionIssue
    else:
        try:
            resp = req.json()
        except (
            ValueError
        ):  # When GBIF throws an error message, it's plain text (not JSON)
            raise GBIFApiError(req.text)

        c = resp.get("count")
        if c is None:
            # GBIF omits "count" only when the query returns no results at all.
            if resp.get("endOfRecords") and not resp.get("results"):
                c = 0
            else:
                raise GBIFApiError(
                    f"Unexpected GBIF response (missing 'count'): {req.text}"
                )

    return c


def get_occurrences_in_batches(filters):
    p = _finalize_filters(filters)

    finished = False
    offset = 0
    current_count = 0
    total_count = count_occurrences(filters)

    if total_count > WARNING_THRESHOLD:
        if not show_warning():
            return  # User chose not to continue

    while not finished:
        p["offset"] = offset
        headers = {
            'User-Agent': 'QGIS Plugin GBIF Occurrences',
            'From': 'https://github.com/BelgianBiodiversityPlatform/qgis-gbif-api'
        }

        req = requests.get(OCCURRENCES_SEARCH_URL, params=p, headers=headers)

        resp = req.json()

        if resp["endOfRecords"]:
            finished = True  # This will be the last turn...

        if finished:
            current_count = total_count
        else:
            current_count = current_count + RECORDS_PER_PAGE

        yield (resp["results"])

        offset = offset + RECORDS_PER_PAGE
