import requests


class RequestHandler:
    def __init__(self, ip_address: str, port: int, https: bool = False):
        self._base = f"{'https' if https else 'http'}://{ip_address}:{port}"

    def get_json(self, uri: str, params: dict = None) -> dict:
        if uri.startswith("/"):
            uri = uri[1:]
        url = f"{self._base}/{uri}"
        res = requests.get(url, params=params)
        if res:
            return res.json()
        return {}

    def get_json_post(self, uri: str, params: dict = None, data: dict = None) -> dict:
        if uri.startswith("/"):
            uri = uri[1:]
        url = f"{self._base}/{uri}"
        res = requests.post(url, params=params, data=data)
        if res:
            return res.json()
        return {}
