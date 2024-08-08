from typing import List


class Netlist:
    def __init__(self, path: str):
        self.netlist_path = path
        self.subckts_names: List[str] = []
        self.vsources_names: List[str] = []
        self.resistors_names: List[str] = []
        self.mosfets_names: List[str] = []
        self.capacitors_names: List[str] = []
        self.commands: List[str] = []
        self.original_string: str = ''

        with open(path, 'r') as f:
            self.original_string = f.read()
