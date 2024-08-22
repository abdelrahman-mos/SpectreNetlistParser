from typing import List
from Device import Device


class Netlist:
    def __init__(self, path: str):
        self.netlist_path = path
        self.subckts_names: List[str] = []
        self.devices: List[Device] = []
        self.full_devices: List[Device] = []
        self.commands: List[str] = []
        self.original_string: str = ''

        with open(path, 'r') as f:
            self.original_string = f.read()
