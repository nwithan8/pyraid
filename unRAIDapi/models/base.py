class BaseObject:
    def __init__(self, data: dict, api):
        self._data = data
        self._api = api