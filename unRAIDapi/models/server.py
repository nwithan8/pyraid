from unRAIDapi.models.base import BaseObject
from unRAIDapi.models.docker import Docker
from unRAIDapi.models.peripherals import PCI, USB
from unRAIDapi.models.vm import VMManager


class Server(BaseObject):
    def __init__(self, ip_address: str, data: dict, api):
        super().__init__(data, api)
        self.ip_address = ip_address
        self._parse_data()
        self._docker = None
        self._vms = None
        self._pcis = None
        self._usbs = None

    def _parse_data(self):
        details = self._data.get('serverDetails', {})
        self.arrayStatus = details.get('arrayStatus')
        self.moverRunning = details.get('moverRunning')
        self.parityCheckRunning = details.get('parityCheckRunning')
        self.title = details.get('title')
        self.cpu = details.get('cpu')
        self.memory = details.get('memory')
        self.motherboard = details.get('motherboard')
        self.diskSpace = details.get('diskSpace')
        self.version = details.get('version')
        self.arrayUsedSpace = details.get('arrayUsedSpace')
        self.arrayTotalSpace = details.get('arrayTotalSpace')
        self.arrayFreeSpace = details.get('arrayFreeSpace')
        self.on = details.get('on')
        self.status = details.get('status')

    @property
    def docker(self):
        if not self._docker:
            self._docker = Docker(data=self._data.get('docker', {}), api=self._api)
        return self._docker

    @property
    def virtual_machines(self):
        if not self._vms:
            self._vms = VMManager(data=self._data.get('vm', {}), api=self._api)
        return self._vms

    @property
    def PCIs(self):
        if not self._pcis:
            self._pcis = [PCI(data=data, api=self._api) for data in self._data.get('pciDetails', [])]
        return self._pcis

    @property
    def USBs(self):
        if not self._usbs:
            self._usbs = [USB(data=data, api=self._api) for data in self._data.get('usbDetails', [])]
        return self._usbs

    def create_virtual_machine(self, **values):
        json_data = self._api._request_handler.get_json_post(uri='api/createVM', data=values)
        return json_data.get('message', {}).get('success')





