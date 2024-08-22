# SpectreNetlistParser
A netlist parser for spectre netlists
## Future Work
- Add terminals to already parsed subckts.
  * This can be useful to apply nets mapping ?
- Parse hierarchical subckts (can be recursive ?).
  * loop through all devices, if a subcircuit call parse_subckt with parent name as the subcircuit that was found.
  * all devices found in the subcircuit will have the model name as <parent_subcircuit>.<device_name>.
  * if another subcircuit was found inside the subcircuit, parse_subckt will be called on that subcircuit (recursively).
  * This could parse all devices, the base of the recursive approach would be to find a subcircuit that doesn't contain any inner subcircuits.
    * This could be broke if a subcircuit references itself ? spectre doesn't allow recursive referencing, then we shouldn't.
