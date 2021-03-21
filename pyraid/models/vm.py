from typing import List

from pyraid.models.base import BaseObject
from pyraid.models.peripherals import USB, PCI


class VMNIC(BaseObject):
    def __init__(self, data: dict, api):
        super().__init__(data, api)
        self.mac = data.get('mac')
        self.network = data.get('network')


class VMShare(BaseObject):
    def __init__(self, data: dict, api):
        super().__init__(data, api)
        self.source = data.get('source')
        self.target = data.get('target')


class VMDisk(BaseObject):
    def __init__(self, data: dict, api):
        super().__init__(data, api)
        self.select = data.get('select')
        self.image = data.get('image')
        self.driver = data.get('driver')
        self.bus = data.get('bus')
        self.size = data.get('size')


class VMTemplate(BaseObject):
    def __init__(self, data: dict, api):
        super().__init__(data, api)
        self._parse_data()
        self._disks = []
        self._shares = []
        self._usbs = []
        self._pcis = []
        self._nics = []

    def _parse_data(self):
        self.os = self._data.get('template_os')
        self.domain_type = self._data.get('domain_type')
        self.name = self._data.get('template_name')
        self.icon = self._data.get('template_icon')
        self.persistent = self._data.get('domain_persistent')
        self.clock = self._data.get('domain_clock')
        self.architecture = self._data.get('domain_arch')
        self.domain_old_name = self._data.get('domain_oldname')
        self.domain_name = self._data.get('domain_name')
        self.description = self._data.get('domain_desc')
        self.cpu_mode = self._data.get('domain_cpumode')
        self.memory = int(self._data.get('domain_mem', 0))
        self.max_memory = int(self._data.get('domain_maxmem', 0))
        self.machine = self._data.get('domain_machine')
        self.hyper_v = self._data.get('domain_hyperv')
        self.usb_mode = self._data.get('domain_usbmode')
        self.ovmf = self._data.get('domain_ovmf')
        self.cd_rom = self._data.get('media_cdrom')
        self.cd_rom_bus = self._data.get('media_cdrombus')
        self.drivers = self._data.get('media_drivers')
        self.drivers_bus = self._data.get('media_driversbus')
        self.gpu_bios = self._data.get('gpu_bios')
        self.nic_0_mac = self._data.get('nic_0_mac')
        self.vcpus = self._data.get('vcpus', [])

    @property
    def disks(self):
        if not self._disks:
            self._disks = [VMDisk(data=data, api=self._api) for data in self._data.get('disks', [])]
        return self._disks

    @property
    def shares(self):
        if not self._shares:
            self._shares = [VMShare(data=data, api=self._api) for data in self._data.get('shares', [])]
        return self._shares

    @property
    def USBs(self):
        if not self._usbs:
            self._usbs = [USB(data=data, api=self._api) for data in self._data.get('usbs', [])]
        return self._usbs

    @property
    def PCIs(self):
        if not self._pcis:
            self._pcis = [PCI(data=data, api=self._api) for data in self._data.get('pcis', [])]
        return self._pcis

    @property
    def NICs(self):
        if not self._nics:
            self._nics = [VMNIC(data=data, api=self._api) for data in self._data.get('nics', [])]
        return self._nics


class VMHardDrive(BaseObject):
    def __init__(self, data: dict, api):
        super().__init__(data, api)
        self.path = data.get('path')
        self.interface = data.get('interface')
        self.used = data.get('used')


class VM(BaseObject):
    def __init__(self, id: str, data: dict, api):
        super().__init__(data, api)
        self.id = id
        self._parse_data()
        self._hard_drives = []
        self._template = None

    def _parse_data(self):
        self.name = self._data.get('name')
        self.status = self._data.get('status')
        self.icon = self._data.get('icon')
        self.coreCount = int(self._data.get('coreCount', 0))
        self.ramAllocation = self._data.get('ramAllocation')
        self.primaryGPU = self._data.get('primaryGPU')
        self.xml = self._data.get('xml')
        self.diskCountSize = self._data.get('hddAllocation', {}).get('total')

    @property
    def hard_drives(self):
        if not self._hard_drives:
            self._hard_drives = [VMHardDrive(data=hdd_data, api=self._api) for hdd_data in
                                 self._data.get('hddAllocation', {}).get('all', [])]
        return self._hard_drives

    @property
    def template(self):
        if not self._template:
            self._template = VMTemplate(data=self._data.get('edit', {}), api=self._api)
        return self._template

    def _control(self, action: str):
        if not self.id:
            return False
        data = {
            'id': self.id,
            'action': action,
            'server': self._api._server_creds.ip_address,
            'auth': self._api._server_cred._creds
        }
        json_data = self._api._request_handler.get_json_post(uri='api/vmStatus', data=data)
        return json_data.get('message', {}).get('success')

    def start(self):
        return self._control(action='domain-start')

    def stop(self):
        return self._control(action='domain-stop')

    def pause(self):
        return self._control(action='domain-paus')

    def resume(self):
        return self._control(action='domain-resume')

    def force_stop(self):
        return self._control(action='domain-destroy')

    def restart(self):
        return self._control(action='domain-restart')

    def hibernate(self):
        return self._control(action='domain-pmsuspend')

    def add_usb(self, usb_id: str):
        if not self.id:
            return False
        data = {
            'id': self.id,
            'usbId': usb_id,
            'server': self._api._server_creds.ip_address,
            'auth': self._api._server_cred._creds
        }
        json_data = self._api._request_handler.get_json_post(uri='api/usbAttach', data=data)
        return json_data.get('message', {}).get('success')

    def add_pci(self, pci_ids: List[str]):
        if not self.id:
            return False
        data = {
            'id': self.id,
            'pciIds': pci_ids,
            'server': self._api._server_creds.ip_address,
            'auth': self._api._server_cred._creds
        }
        json_data = self._api._request_handler.get_json_post(uri='api/pciAttach', data=data)
        return json_data.get('message', {}).get('success')

    def swap_gpu(self, second_vm_id: str, pci_ids: List[str] = None):
        if not self.id:
            return False
        data = {
            'id1': self.id,
            'id2': second_vm_id,
            'server': self._api._server_creds.ip_address,
            'auth': self._api._server_cred._creds
        }
        if pci_ids:
            data['pciIds'] = pci_ids
        json_data = self._api._request_handler.get_json_post(uri='api/gpuSwap', data=data)
        return json_data.get('message', {}).get('success')

    def edit(self, **values):
        if not self.id:
            return False
        data = {
            'id': self.id,
            'edit': values,
            'server': self._api._server_creds.ip_address,
            'auth': self._api._server_cred._creds
        }
        json_data = self._api._request_handler.get_json_post(uri='api/editVM', data=data)
        return json_data.get('message', {}).get('success')


class VMManager(BaseObject):
    def __init__(self, data: dict, api):
        super().__init__(data, api)
        self.extras = data.get('extras')
        self._vms = []

    @property
    def vms(self):
        if not self._vms:
            details = self._data.get('details', {})
            for vm_id, vm_data in details.items():
                self._vms.append(VM(id=vm_id, data=vm_data, api=self._api))
        return self._vms
