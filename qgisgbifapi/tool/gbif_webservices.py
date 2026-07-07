from urllib.parse import urljoin
from qgis.PyQt.QtWidgets import QMessageBox
import requests

from qgisgbifapi.__about__ import (
    __api_endpoint__,
    __api_occurrences_search__,
    __api_per_page_records__,  # Maximum currently supported by API
    __api_warning_threshold__,  # Threshold for showing the warning
)

OCCURRENCES_SEARCH_URL = urljoin(__api_endpoint__, __api_occurrences_search__)
# (connect, read) timeout in seconds for every GBIF request, so the plugin
# never hangs indefinitely on a stalled connection. A generous read timeout
# leaves room for GBIF to assemble a full page (300 records) under load.
REQUEST_TIMEOUT = (10, 60)


class ConnectionIssue(Exception):
    pass


class GBIFApiError(Exception):
    pass


def _finalize_filters(filters):
    fixed_filters = {"hasCoordinate": "true", "limit": __api_per_page_records__}  # noqa: E501
    return dict(list(filters.items()) + list(fixed_filters.items()))


def show_warning():
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setText(
        f"The number of results is very large (> {__api_warning_threshold__}). Do you want to continue?"  # noqa: E501
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
        req = requests.get(
            OCCURRENCES_SEARCH_URL,
            params=p,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
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

    if total_count > int(__api_warning_threshold__):
        if not show_warning():
            return  # User chose not to continue

    while not finished:
        p["offset"] = offset
        headers = {
            'User-Agent': 'QGIS Plugin GBIF Occurrences',
            'From': 'https://github.com/BelgianBiodiversityPlatform/qgis-gbif-api'  # noqa: E501
        }

        req = requests.get(
            OCCURRENCES_SEARCH_URL,
            params=p,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )

        resp = req.json()

        if resp["endOfRecords"]:
            finished = True  # This will be the last turn...

        if finished:
            current_count = total_count
        else:
            current_count = current_count + int(__api_per_page_records__)

        yield (resp["results"])

        offset = offset + int(__api_per_page_records__)
