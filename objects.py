class VM:
    def __init__(self, data):
        self.name = data.get('Name')
        self.state = data.get('State')
        self.disks = data.get('Disks')
        self.autostart = data.get('Autostart')
