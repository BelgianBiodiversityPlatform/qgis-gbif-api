# Import basic libs
import json

# Import PyQt libs
from qgis.PyQt.QtCore import QObject, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest
from qgis.core import QgsNetworkAccessManager

from qgisgbifapi.tool import add_gbif_occ_to_layer
from qgisgbifapi.__about__ import (
    __api_endpoint__,
    __api_occurrences_search__,
    __api_per_page_records__,
)


class BatchRequest(QObject):
    finished_dl = pyqtSignal()
    """Used to make web request.
    :param
        url: The web request url
        manager: a QgsNetworkAccessManager to realize the network request
        """

    def __init__(
        self,
        manager: QgsNetworkAccessManager = None,
        dlg=None,
    ):
        super().__init__()
        self.network_manager = manager
        self.dlg = dlg

        self.total_pages = 0
        self._pending_pages = 0
        self._pending_obs = 0
        self._pending_downloads = 0

    @property
    def pending_pages(self):
        return self._pending_pages

    @property
    def pending_obs(self):
        return self._pending_obs

    @property
    def pending_downloads(self):
        return self._pending_downloads

    def create_url(self, params):
        request_url = __api_endpoint__ + __api_occurrences_search__ + "?"
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

    def download(self, params, layer, total_obs):
        request_url = self.create_url(params)
        request = QNetworkRequest(QUrl(request_url))
        request.setRawHeader(
            b"User-Agent",
            bytes('QGIS Plugin GBIF Occurrences', encoding="utf-8"),
        )
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")  # noqa: E501
        reply = self.network_manager.get(request)
        reply.finished.connect(
            lambda: self.handle_finished(
                reply,
                params,
                layer,
                total_obs
            )
        )
        self._pending_downloads += 1
        self._pending_pages += 1

    def handle_finished(self, reply, params, layer, total_obs):
        self._pending_downloads -= 1
        if reply.error() != QNetworkReply.NetworkError.NoError:
            print(
                f"code: {reply.error()} message: {reply.errorString()}"
            )
        else:
            # Decode data fetch from the get request and create a dictionnary.
            data_request = reply.readAll().data().decode()
            resp = json.loads(data_request)
        if self.pending_downloads == 0:
            if self.pending_pages > self.total_pages:
                self.total_pages = 0
                self._pending_pages = 0
                self._pending_obs = 0
                self.finished_dl.emit()
            else:
                if total_obs < int(__api_per_page_records__):
                    self._pending_obs = total_obs
                elif total_obs - self._pending_obs < int(__api_per_page_records__):  # noqa: E501
                    self._pending_obs = self.pending_obs + total_obs - self.pending_obs  # noqa: E501
                else:
                    self._pending_obs += int(__api_per_page_records__)
                self.dlg.show_progress(self._pending_obs, total_obs)
                add_gbif_occ_to_layer(resp["results"], layer)
                if self.dlg.stop:
                    self.dlg.stop = False
                    self.total_pages = 0
                    self._pending_pages = 0
                    self._pending_obs = 0
                    self.finished_dl.emit()
                else:
                    params["offset"] = self._pending_obs
                    self.download(params, layer, total_obs)
        reply.deleteLater()
