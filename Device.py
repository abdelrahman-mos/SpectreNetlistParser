from typing import List


class Device:
    def __init__(self):
        self.terminals: List[str] = []
        self.name: str = ''
        self.parent_subckt: str = ''
