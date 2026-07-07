# Import basic libs
import json

# Import PyQt libs
from qgis.PyQt.QtCore import QObject, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest
from qgis.core import QgsNetworkAccessManager


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

        self.nb_obs = 0
        self._pending_downloads = 0

    @property
    def pending_downloads(self):
        return self._pending_downloads

    def create_url(self, api_url, occurrences_search, params):
        request_url = api_url + occurrences_search + "?"
        for param in params:
            if isinstance(params[param], list):
                for elem in params[param]:
                    request_url = request_url + str(param) + "=" + str(elem) + "&"  # noqa: E501
            elif params[param] == "":
                pass
            elif params[param] is None:
                pass
            else:
                request_url = request_url + str(param) + "=" + str(params[param]) + "&"  # noqa: E501
        return request_url[:-1]

    def download(self, api_url, occurrences_search, params):
        request_url = self.create_url(api_url, occurrences_search, params)
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
