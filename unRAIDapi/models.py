from unRAIDapi import soup


class Disk:
    def __init__(self, data: dict):
        self._data = data
        self.device = data.get('device')
        self.bus = data.get('bus')
        self.capacity = data.get('capacity')
        self.allocation = data.get('allocation')

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.device}>"


class VM:
    def __init__(self, data: dict):
        self._data = data
        self.name = data.get('Name')
        self.state = data.get('State')
        self._disks = []
        self.autostart = data.get('Autostart')
        self.cpu_count = data.get('CPU')
        self.uuid = data.get('UUID')
        self.memory = data.get('Memory')
        self.vnc_port = data.get('VNC')

    @property
    def disks(self):
        if not self._disks:
            self._disks = [Disk(disk) for disk in self._data.get('Disks', [])]
        return self._disks

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"


class Share:
    def __init__(self, row: str):
        self._row = row
        self._parse_row()
        self._data = {}
        self.name = self._data.get('Name')
        self.description = self._data.get('Desc')
        self.smb_setting = ('Off' if self._data.get('SMB') == '-' else self._data.get('SMB'))
        self.nfs_setting = ('Off' if self._data.get('NFS') == '-' else self._data.get('NFS'))
        self.afp_setting = ('Off' if self._data.get('AFP') == '-' else self._data.get('AFP'))
        self.cache_setting = self._data.get('Cache')
        self.size = None
        self.free = self._data.get('Free')
        self.files_protected = self._data.get('Secured')

    def _parse_row(self):
        columns = soup.parse_table_row(self._row)
        secured = False
        if columns[0].startswith("All files protected"):
            columns[0] = columns[0][19:]
            secured = True
        self._data = {'Name': columns[0],
                      'Desc': columns[1],
                      'SMB': columns[2],
                      'NFS': columns[3],
                      'AFP': columns[4],
                      'Cache': columns[5],
                      'Size': columns[6],
                      'Free': columns[7],
                      'Secured': secured}

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"


class ParityHistoryEntry:
    def __init__(self, row: str):
        self._row = row
        self._parse_row()

    def _parse_row(self):
        columns = soup.parse_table_row(self._row)
        self.date = columns[0]
        self.duration = columns[1]
        self.speed = columns[2]
        self.status = columns[3]
        self.errors = columns[4]
        self.elapsed_time = columns[5]
        if len(columns) >= 8:
            self.increments = columns[6]
            self.type = columns[7]

    def __getattr__(self, item):
        return None

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.date}>"
