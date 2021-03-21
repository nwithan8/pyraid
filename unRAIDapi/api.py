from typing import Union, List

from unRAIDapi import utils
from unRAIDapi.models.server import Server
from unRAIDapi.request_handler import RequestHandler


class ServerConnectionDetails:
    def __init__(self, ip_address: str, username: str, password: str):
        self.ip_address = ip_address
        self._creds = utils.encode_username_password(username=username, password=password)


class API:
    def __init__(self, ip_address: str, port: int, username: str, password: str, https: bool = False):
        self._request_handler = RequestHandler(ip_address=ip_address, port=port, https=https)
        self._server_creds = ServerConnectionDetails(ip_address=ip_address, username=username, password=password)

    @property
    def servers(self):
        json_data = self._request_handler.get_json(uri='api/getServers')
        servers = []
        for ip_address, server_data in json_data.get('servers', {}).items():
            servers.append(Server(ip_address=ip_address, data=server_data, api=self))
        return servers

    def add_server(self, server_url: str, username: str, password: str):
        creds_string = utils.encode_username_password(username=username, password=password)
        data = {
            'ip': server_url,
            'authToken': creds_string
        }
        json_data = self._request_handler.get_json_post(uri='api/login', data=data)
        return json_data.get('message') == 'connected'
