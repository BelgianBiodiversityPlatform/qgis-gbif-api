# Import basic libs
import json

# Import PyQt libs
from qgis.PyQt.QtCore import QObject, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest
from qgis.PyQt.QtWidgets import QDialog
from qgis.core import QgsNetworkAccessManager, QgsProject

from qgisgbifapi.tool import add_gbif_occ_to_layer, create_url
from qgisgbifapi.__about__ import __api_per_page_records__


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
        dlg: QDialog = None,
        project: QgsProject = None,
    ):
        super().__init__()
        self.project = project
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

    def download(self, params, layer, total_obs):
        request_url = create_url(params)
        request = QNetworkRequest(QUrl(request_url))
        # Add header to the request to add user agent
        request.setRawHeader(
            b"User-Agent",
            bytes('QGIS Plugin GBIF Occurrences', encoding="utf-8"),
        )
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")  # noqa: E501
        # launch request
        reply = self.network_manager.get(request)
        # set function when finished signal is emited
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
            self.dlg.connection_error_message()
            self._pending_downloads = 0
            self._pending_pages = self.total_pages + 1
        else:
            # Decode data fetch from the get request and create a dictionnary.
            data_request = reply.readAll().data().decode()
            resp = json.loads(data_request)

        if self.pending_downloads == 0:
            # if no other downloads are needed, emit finished_dl signal
            if self.pending_pages > self.total_pages:
                self.total_pages = 0
                self._pending_pages = 0
                self._pending_obs = 0
                self.finished_dl.emit()
            else:
                # get the number of downloaded data for the progress bar
                if total_obs < int(__api_per_page_records__):
                    self._pending_obs = total_obs
                elif total_obs - self._pending_obs < int(__api_per_page_records__):  # noqa: E501
                    self._pending_obs = self.pending_obs + total_obs - self.pending_obs  # noqa: E501
                else:
                    self._pending_obs += int(__api_per_page_records__)
                self.dlg.show_progress(self._pending_obs, total_obs)
                # add data fetch from api to result layer
                add_gbif_occ_to_layer(
                    self.project,
                    resp["results"],
                    layer,
                    self.dlg.minimalCheckBox.isChecked(),
                    self.dlg.crs_selection.crs(),
                )
                # if the button stop is pressed emit the finished_dl signal
                if self.dlg.stop:
                    self.dlg.stop = False
                    self.total_pages = 0
                    self._pending_pages = 0
                    self._pending_obs = 0
                    self.finished_dl.emit()
                else:
                    # change offset number
                    # launch next download with new parameters
                    params["offset"] = self._pending_obs
                    self.download(params, layer, total_obs)
        reply.deleteLater()
