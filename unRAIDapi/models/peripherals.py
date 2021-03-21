from unRAIDapi.models.base import BaseObject


class PCI(BaseObject):
    def __init__(self, data: dict, api):
        super().__init__(data, api)
        self.gpu = data.get('gpu')
        self.sound = data.get('sound')
        self.id = data.get('id')
        self.name = data.get('name')
        self.checked = data.get('checked')
        self.position = data.get('position')
        self.model = data.get('model')
        self.keymap = data.get('keymap')
        self.bios = data.get('bios')


class USB(BaseObject):
    def __init__(self, data: dict, api):
        super().__init__(data, api)
        self.id = data.get('id')
        self.name = data.get('name')
