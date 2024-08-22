from typing import List


class Device:
    def __init__(self):
        self.terminals: List[str] = []
        self.name: str = ''
        self.parent_subckt: str = ''
        self.model: str = ''
        self.type: str = ''


class SubCircuit(Device):
    def __init__(self):
        super().__init__()
        self.devices: List[str] = []
        self.type: str = 'SubCircuit'

