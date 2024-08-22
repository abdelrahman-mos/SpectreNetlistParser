# SpectreNetlistParser
A netlist parser for spectre netlists
## Return Shape
- A Netlist Class in the shape of:
  ```
  Netlist:
   Netlist_path: str
   subckt_names: List[str]
   devices: List[Device]
   full_devices_dict: Dict[str, Device]
   commands: List[str]
   original_string: str
  ```
