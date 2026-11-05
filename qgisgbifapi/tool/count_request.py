# Import basic libs
import json

# Import PyQt libs
from qgis.PyQt.QtCore import QObject, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest
from qgis.PyQt.QtWidgets import QDialog
from qgis.core import QgsNetworkAccessManager

from qgisgbifapi.tool import create_url


class CountRequest(QObject):
    finished_dl = pyqtSignal()
    """Used to make web request.
    :param
        url: The web request url
        manager: a QgsNetworkAccessManager to realize the network request
        """

    def __init__(
        self, dlg: QDialog = None, manager: QgsNetworkAccessManager = None
    ):
        super().__init__()
        self.dlg = dlg
        self.network_manager = manager

        self.taxon_key = None
        self.scientific_name = None
        self.params = None

        self.nb_obs = 0
        self._pending_downloads = 0

    @property
    def pending_downloads(self):
        return self._pending_downloads

    def download(self, params):
        # set object property
        self.taxon_key = params["taxonKey"]
        self.scientific_name = params["scientificName"]
        self.params = params
        self.params['offset'] = 0
        # use parameters selected by user to create download url
        request_url = create_url(self.params)
        request = QNetworkRequest(QUrl(request_url))
        # add user-agent to identify the plugin
        request.setRawHeader(
            b"User-Agent",
            bytes('QGIS Plugin GBIF Occurrences', encoding="utf-8"),  # noqa: E501
        )
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")  # noqa: E501
        # launch download request
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self.handle_finished(reply))
        self._pending_downloads += 1

    def handle_finished(self, reply):
        self._pending_downloads -= 1
        if reply.error() != QNetworkReply.NetworkError.NoError:
            print(
                f"code: {reply.error()} message: {reply.errorString()}"  # noqa: E501
            )
            self.dlg.connection_error_message()
        else:
            # Decode data fetch from the get request and create a dictionnary.
            data_request = reply.readAll().data().decode()
            res = json.loads(data_request)
            # Get the observation number in the extent based on filters.
            self.nb_obs = res["count"]
            if self.pending_downloads == 0:
                self.finished_dl.emit()
        reply.deleteLater()
