from typing import Union, List

import requests
import re
import json

from unRAIDapi.models import Share, VM, ParityHistoryEntry
from unRAIDapi import soup


class Server:

    # TODO Map all of the JSON vars

    def __init__(self, address, username, password, api_key=None):
        self.address = address
        self._username = username
        self._password = password
        self._api_key = api_key
        self._session = None
        self._config = None
        self._load_config()
        self._csrf = None
        self._mac = None
        self._vms = []

    def _get(self, endpoint=None, count=0) -> Union[requests.Response, None]:
        res = self.session.get(url=f'{self.address}{("/" + endpoint if endpoint else "")}')
        if res.status_code != 200:
            # Re-login if session expires
            # Stop trying if three failed re-login attempts, reset session
            if count > 3:
                self._session = None
                print("Session expired and/or credentials changed.")
                return None
            return self._get(endpoint, count=count + 1)
        return res

    @property
    def session(self) -> requests.Session:
        if not self._session:
            self._session = self._connect_to_session()
        return self._session

    def _connect_to_session(self) -> Union[requests.Session, None]:
        with requests.Session() as sess:
            payload = {'username': self._username, 'password': self._password}
            print(self.address)
            res = sess.post(f'{self.address}/login', data=payload)
            if res.status_code == 200:
                return sess
            return None

    @property
    def config(self) -> dict:
        if not self._config:
            html = self._get().text
            temp_vars = re.search(r'display[\s\S]+vars\s+=(.+);', html)[1]
            self._config = json.loads(temp_vars)
        return self._config

    def _load_config(self):
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

    @property
    def CSRF_token(self):
        if not self._csrf:
            self._csrf = self.config.get('csrf_token')
        return self._csrf

    @property
    def MAC(self) -> Union[str, None]:
        if not self._mac:
            s = soup.get_soup(self._get(endpoint='Settings/NetworkSettings').text)
            self._mac = s.find(id='view-eth0').find_all('dd')[0].getText()
        return self._mac

    def _parse_vms(self):
        vms = []
        s = soup.get_soup(self._get(endpoint='plugins/dynamix.vm.manager/include/VMMachines.php').text)
        names_table = s.find_all('span', {'class': 'outer'})
        autostarts = s.find_all('input', {'class': 'autostart'})
        disks_table = s.find_all('table', {'class': 'tablesorter domdisk'})
        cpus = s.find_all('a', {'style': 'cursor:pointer'})
        sortables = s.find_all('tr', {'class': 'sortable'})
        if len(names_table) == len(disks_table):
            for i in range(0, len(names_table)):
                vm_disks = []
                for disk in soup.parse_table_rows(disks_table[i].find_all('tbody')[0]):
                    details = soup.parse_table_row(disk)
                    vm_disks.append(
                        {'device': details[0],
                         'bus': details[1],
                         'capacity': details[2],
                         'allocation': details[3]})
                vm_name = names_table[i].find('span', {'class': 'inner'})
                vms.append({'Name': vm_name.find('a').getText(),
                            'State': vm_name.find('span', {'class': 'state'}).getText(),
                            'Disks': vm_disks,
                            'Autostart': autostarts[i].has_attr('checked'),
                            'CPU': int(cpus[i].getText()),
                            'Memory': sortables[i].find_all('td')[3].getText(),
                            })
        return vms

    @property
    def VMs(self) -> List[VM]:
        if not self._vms:
            for vm in self._parse_vms():
                self._vms.append(VM(data=vm))
        return self._vms

    @property
    def array(self):
        return self._get().text

    @property
    def parity_history(self):
        data = []
        parity_history_table = soup.get_soup(self._get(endpoint='webGui/include/ParityHistory.php').text).find_all('tbody')[0]
        for row in soup.parse_table_rows(table=parity_history_table):
            data.append(ParityHistoryEntry(row=row))
        return data

    @property
    def shares(self):
        shares = []
        shares_table = soup.get_soup(self._get(endpoint='webGui/include/ShareList.php?compute=no&path=Shares&scale=-1&numbers=.%2C').text)
        for row in soup.parse_table_rows(table=shares_table):
            shares.append(Share(row=row))
        return shares
