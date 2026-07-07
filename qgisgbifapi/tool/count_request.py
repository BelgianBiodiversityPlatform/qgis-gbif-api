# Import basic libs
import json

# Import PyQt libs
from qgis.PyQt.QtCore import QObject, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest
from qgis.core import QgsNetworkAccessManager

from qgisgbifapi.__about__ import (
    __api_endpoint__,
    __api_occurrences_search__,
)


class CountRequest(QObject):
    finished_dl = pyqtSignal()
    """Used to make web request.
    :param
        url: The web request url
        manager: a QgsNetworkAccessManager to realize the network request
        """

    def __init__(
        self, manager: QgsNetworkAccessManager = None
    ):
        super().__init__()
        self.network_manager = manager

        self.params = None
        self.nb_obs = 0
        self._pending_downloads = 0

    @property
    def pending_downloads(self):
        return self._pending_downloads

    def create_url(self):
        request_url = __api_endpoint__ + __api_occurrences_search__ + "?"
        for param in self.params:
            if isinstance(self.params[param], list):
                for elem in self.params[param]:
                    request_url = request_url + str(param) + "=" + str(elem) + "&"  # noqa: E501
            elif self.params[param] == "":
                pass
            elif self.params[param] is None:
                pass
            else:
                request_url = request_url + str(param) + "=" + str(self.params[param]) + "&"  # noqa: E501
        return request_url[:-1]

    def download(self, params):
        self.params = params
        request_url = self.create_url()
        request = QNetworkRequest(QUrl(request_url))
        request.setRawHeader(
            b"User-Agent",
            bytes('QGIS Plugin GBIF Occurrences', encoding="utf-8"),  # noqa: E501
        )
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")  # noqa: E501
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self.handle_finished(reply))
        self._pending_downloads += 1

    def handle_finished(self, reply):
        self._pending_downloads -= 1
        if reply.error() != QNetworkReply.NetworkError.NoError:
            print(
                f"code: {reply.error()} message: {reply.errorString()}"  # noqa: E501
            )
        else:
            # Decode data fetch from the get request and create a dictionnary.
            data_request = reply.readAll().data().decode()
            res = json.loads(data_request)
            # Get the observation number in the extent based on filters.
            self.nb_obs = res["count"]
        reply.deleteLater()
        if self.pending_downloads == 0:
            self.finished_dl.emit()
