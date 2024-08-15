from typing import List, Dict, Tuple
from Netlist import Netlist
from Device import Device


class SpectreNetlistParser:
    supported_analogLib = ['vsource', 'resistor', 'vcvs', 'cvcs', 'cccs', 'ccvs', 'capacitor', 'transformer']
    supported_modelnames = ['nch', 'pch', 'nch_lvt', 'pch_lvt']
    supported_spectreCommands = ['include', 'simulator', 'global', 'parameters', 'save']
    supported_commands = ['tran', 'dc', 'ac', 'info', 'noise', 'xf', 'pss', 'options']

    @staticmethod
    def parse_netlist(path: str):
        output_netlist = Netlist(path)
        original_text = output_netlist.original_string.lower()
        original_text_no_comments = SpectreNetlistParser.remove_comments(original_text)
        original_text_no_multiline = SpectreNetlistParser.remove_multilines(original_text_no_comments)
        subckts_names = SpectreNetlistParser.parse_subckts_names(original_text_no_multiline)
        original_text_no_subckts = SpectreNetlistParser.remove_subckts(original_text_no_multiline)
        original_text_no_commands, commands = SpectreNetlistParser.remove_commands(original_text_no_subckts)
        highest_hierarchy_devices = SpectreNetlistParser.parse_highest_hierarchy(original_text_no_commands,
                                                                                 subckts_names)
        output_netlist.subckts_names = subckts_names
        output_netlist.devices = highest_hierarchy_devices
        output_netlist.commands = commands
        return output_netlist

    @staticmethod
    def remove_comments(original_text: str) -> str:
        if not original_text:
            raise ValueError
        output_text = ''
        lines = original_text.splitlines()
        for line in lines:
            if not line.startswith('//'):
                output_text += line + '\n'
        return output_text

    @staticmethod
    def remove_multilines(original_text_no_comments: str) -> str:
        output_text = ''
        lines = original_text_no_comments.splitlines()
        netlist_lines = iter(lines)
        for line in netlist_lines:
            if line.endswith("\\"):
                while line.endswith("\\"):
                    output_text += line[:-1].strip() + ' '
                    line = next(netlist_lines)
            output_text += line.strip() + '\n'

        return output_text

    @staticmethod
    def parse_subckts_names(original_text_no_multiline: str) -> List[str]:

        subckt_names = []
        inside_subckt = False
        lines = original_text_no_multiline.splitlines()

        for line in lines:
            if line.startswith('subckt '):
                inside_subckt = True
                subckt_name = line.split(' ')[1]
                subckt_names.append(subckt_name)

            elif line.startswith('ends '):
                inside_subckt = False

        return subckt_names

    @staticmethod
    def remove_subckts(original_text: str) -> str:
        lines = original_text.splitlines()
        output_text = ''
        inside_subckt = False

        for line in lines:
            if line.startswith('subckt '):
                inside_subckt = True
            elif line.startswith('ends '):
                inside_subckt = False
                continue

            if not inside_subckt:
                output_text += line+'\n'
        return output_text

    @staticmethod
    def remove_commands(original_text_no_subckts: str) -> Tuple[str, List[str]]:
        output_text = ''
        commands: List[str] = []
        lines = original_text_no_subckts.splitlines()
        empty_line = False
        for line in lines:
            cond = any(line.strip().startswith(cmd) for cmd in SpectreNetlistParser.supported_spectreCommands)
            if cond:
                commands.append(line)
                continue
            cmd_line = ' '.join(line.split(' ')[1:]).strip()
            cond = any(cmd_line.startswith(cmd) for cmd in SpectreNetlistParser.supported_commands)
            if cond:
                commands.append(line)
                continue

            if line:
                empty_line = False

            if not line and not empty_line:
                empty_line = True
                output_text += line + '\n'
                continue

            if not empty_line:
                output_text += line + '\n'

        return output_text, commands

    @staticmethod
    def parse_highest_hierarchy(original_text_no_commands: str, subckts_names: List[str]) -> List[Device]:
        lines = original_text_no_commands.splitlines()
        output_devices: List[Device] = []
        for line in lines:
            parsed_device = SpectreNetlistParser.parse_single_device(line, subckts_names)
            if parsed_device:
                output_devices.append(parsed_device)

        return output_devices

    @staticmethod
    def parse_single_device(line: str, subckts_names: List[str]) -> Device:
        line_no_braces = line.replace('( ', '(').replace(' )', ')').replace('(', '').replace(')', '')
        split_equal_line = line_no_braces.strip().split('=')
        split_line = split_equal_line[0].split(' ')

        if len(split_equal_line) > 1:
            device_model = split_line[-2]
        else:
            device_model = split_line[-1]

        if not device_model:
            return None

        device_type = None
        if device_model in subckts_names:
            device_type = 'SubCircuit'

        if device_model in SpectreNetlistParser.supported_analogLib:
            device_type = 'AnalogLib'

        if device_model in SpectreNetlistParser.supported_modelnames:
            device_type = 'Mosfet'

        if not device_type:
            raise TypeError('Unsupported device')

        device = Device()
        device.model = device_model
        device.name = split_line[0]
        device.terminals = split_line[1:-2]
        device.type = device_type
        return device


if __name__ == '__main__':
    parsed_netlist = SpectreNetlistParser.parse_netlist(
        'D:\\Projects\\SpectreNetlistParser\\Testing_netlists\\divider_new_netlist.scs')
    x = 1
