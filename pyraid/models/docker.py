from pyraid.models.base import BaseObject


class DockerImage(BaseObject):
    def __init__(self, data: dict, api):
        super().__init__(data, api)


class DockerContainer(BaseObject):
    def __init__(self, id: str, data: dict, api):
        super().__init__(data, api)
        self.id = id
        self._parse_data()

    def _parse_data(self):
        self.imageUrl = self._data.get('imageUrl')
        self.name = self._data.get('imageUrl')
        self.status = self._data.get('imageUrl')
        self.tag = self._data.get('imageUrl')
        self.upToDate = (self._data.get('imageUrl') == 'up-to-date')


class Docker(BaseObject):
    def __init__(self, data: dict, api):
        super().__init__(data, api)
        self._details = data.get('details', {})
        self._images = []
        self._containers = []

    @property
    def images(self):
        if not self._images:
            self._images = [DockerImage(data=image_data, api=self._api) for image_data in self._details.get('images', {}).values()]
        return self._images

    @property
    def containers(self):
        if not self._containers:
            self._containers = [DockerContainer(id=container_id, data=container_data, api=self._api) for container_id, container_data in self._details.get('containers', {}).items()]
        return self._containers

