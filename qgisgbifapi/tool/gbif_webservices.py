from qgis.PyQt.QtWidgets import QMessageBox

from qgisgbifapi.__about__ import (
    __api_per_page_records__,  # Maximum currently supported by API
    __api_warning_threshold__,  # Threshold for showing the warning
)


class ConnectionIssue(Exception):
    pass


class GBIFApiError(Exception):
    pass


def _finalize_filters(filters):
    fixed_filters = {
        "hasCoordinate": "true",
        "limit": __api_per_page_records__
    }
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
