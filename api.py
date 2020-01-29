import requests
import re
import json
from html2json import collect
from bs4 import BeautifulSoup as bs
from objects import VM


def connect(address, username, password):
    with requests.Session() as s:
        payload = {'username': username, 'password': password}
        res = s.post('{}/login'.format(address), data=payload)
        if res.status_code == 200:
            return s
        return None


def _soup(html):
    return bs(html, 'html.parser')


class Server:

    # TODO Map all of the JSON vars

    def __init__(self, address, username, password):
        self.address = address
        self.username = username
        self.password = password
        self.session = connect(self.address, self.username, self.password)
        self.config = None
        self.config = self.getConfig()
        self.name = None
        self.version = None
        self.max_array_size = None
        self.max_cache_size = None
        self.timezone = None
        self.description = None
        self.security = None
        self.workgroup = None
        self.domain = None
        self.domain_short = None
        self.ssl = None
        self.port = None
        self.port_ssl = None
        self.telnet = None
        self.telnet_port = None
        self.ssh = None
        self.ssh_port = None
        self.device_count = None
        self.flash_guid = None
        self.flash_product = None
        self.flash_vendor = None
        self.registration = None
        self.registration_type = None
        self.data_disk_count = None
        self.disabled_disk_count = None
        self.invalid_disk_count = None
        self.missing_disk_count = None
        self.csrf = None
        self.csrf = self.getCSRFToken()
        self.mac = None
        self.mac = self.getMAC()
        self.vms = []
        self.vms = self.getVMs()

    def get(self, endpoint=None, count=0):
        res = self.session.get('{}{}'.format(self.address, ('/' + endpoint if endpoint else "")))
        if res.status_code != 200:
            # Re-login if session expires
            # Stop trying if three failed re-login attempts
            if count > 3:
                return "Session expired and/or credentials changed."
            self.session = connect(self.address, self.username, self.password)
            return self.get(endpoint, count=count + 1)
        return res

    def check(self):
        return self.get().text

    def getConfig(self, update=False):
        if self.config and not update:
            return self.config
        html = self.get().text
        temp_vars = re.search(r'display[\s\S]+vars\s+=(.+);', html)[1]
        self.config = json.loads(temp_vars)
        self.name = self.config.get('NAME')
        self.version = self.config.get('version')
        self.max_array_size = self.config.get('MAX_ARRAYSZ')
        self.max_cache_size = self.config.get('MAX_CACHESZ')
        self.timezone = self.config.get('timeZone')
        self.description = self.config.get('COMMENT')
        self.security = self.config.get('SECURITY')
        self.workgroup = self.config.get('WORKGROUP')
        self.domain = self.config.get('DOMAIN')
        self.domain_short = self.config.get('DOMAIN_SHORT')
        self.ssl = self.config.get('USE_SSL')
        self.port = self.config.get('PORT')
        self.port_ssl = self.config.get('PORTSSL')
        self.telnet = self.config.get('USE_TELNET')
        self.telnet_port = self.config.get('PORTTELNET')
        self.ssh = self.config.get('USE_SSH')
        self.ssh_port = self.config.get('PORTSSH')
        self.device_count = self.config.get('deviceCount')
        self.flash_guid = self.config.get('flashGUID')
        self.flash_product = self.config.get('flashProduct')
        self.flash_vendor = self.config.get('flashVendor')
        self.registration = self.config.get('regGUID')
        self.registration_type = self.config.get('regTy')
        self.data_disk_count = self.config.get('mdNumDisks')
        self.disabled_disk_count = self.config.get('mdNumDisabled')
        self.invalid_disk_count = self.config.get('mdNUmInvalid')
        self.missing_disk_count = self.config.get('mdNumMissing')
        return self.config

    def getCSRFToken(self, update=False):
        if self.csrf and not update:
            return self.csrf
        if self.config and self.config.get('csrf_token'):
            return self.config.get('csrf_token')
        self.config = self.getConfig()
        return self.config.get('csrf_token')

    def getMAC(self, update=False):
        if self.mac and not update:
            return self.mac
        s = _soup(self.get('Settings/NetworkSettings').text)
        mac = s.find(id='view-eth0').find_all('dd')[0].getText()
        if mac:
            return mac
        return None

    def getVMs(self, update=False):
        if self.vms and not update:
            return self.vms
        s = _soup(self.get('plugins/dynamix.vm.manager/include/VMMachines.php').text)
        names = s.find_all('span', {'class': 'outer'})
        autostarts = s.find_all('input', {'class': 'autostart'})
        disks = s.find_all('table', {'class': 'tablesorter domdisk'})
        vms = []
        if len(names) == len(disks):
            for i in range(0, len(names)):
                vm_disks = []
                for disk in disks[i].find('tbody').find_all('tr'):
                    groups = disk.find_all('td')
                    vm_disks.append({'device': groups[0].getText(), 'bus': groups[1].getText(), 'capacity': groups[2].getText(), 'allocation': groups[3].getText()})
                vm_name = names[i].find('span', {'class': 'inner'})
                vm_data = {'Name': vm_name.find('a').getText(), 'State': vm_name.find('span', {'class': 'state'}).getText(), 'Disks': vm_disks, 'Autostart': autostarts[i].has_attr('checked')}
                vms.append(VM(vm_data))
            return vms
        return None

    def getArray(self):
        return self.get().text

    def getParityHistory(self):
        data = []
        for entry in _soup(self.get('webGui/include/ParityHistory.php').text).find_all('tbody')[1].find_all('tr'):
            columns = [td.getText() for td in entry.find_all('td')]
            data.append({'Date': columns[0], 'Duration': columns[1], 'Speed': columns[2], 'Status': columns[3], 'Errors': columns[4], 'Elapsed Time': columns[5], 'Increments': columns[6], 'Type': columns[7]})
        return data
