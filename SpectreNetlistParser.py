from typing import List, Dict, Tuple
from Netlist import Netlist
from Device import Device, SubCircuit


class SpectreNetlistParser:
    supported_analogLib = ['vsource', 'isource', 'resistor', 'vcvs', 'cvcs', 'cccs', 'ccvs', 'capacitor', 'transformer']
    supported_modelnames = ['nch', 'pch', 'nch_lvt', 'pch_lvt']
    supported_spectreCommands = ['include', 'simulator', 'global', 'parameters', 'save']
    supported_commands = ['tran', 'dc', 'ac', 'info', 'noise', 'xf', 'pss', 'options']

    @staticmethod
    def parse_netlist(path: str):
        output_netlist = Netlist(path)
        original_text = output_netlist.original_string.lower()
        original_text_no_comments = SpectreNetlistParser.remove_comments(original_text)
        original_text_no_multiline = SpectreNetlistParser.remove_multilines(original_text_no_comments)
        subckts_names_texts = SpectreNetlistParser.parse_subckts_names_texts(original_text_no_multiline)
        subckts_names = list(subckts_names_texts.keys())
        original_text_no_subckts = SpectreNetlistParser.remove_subckts(original_text_no_multiline)
        original_text_no_commands, commands = SpectreNetlistParser.remove_commands(original_text_no_subckts)
        output_netlist_devices = SpectreNetlistParser.parse_highest_hierarchy(original_text_no_commands, subckts_names)
        output_netlist_devices.extend(SpectreNetlistParser.parse_subckts(output_netlist_devices, subckts_names_texts))
        output_netlist.subckts_names = subckts_names
        output_netlist.devices = output_netlist_devices
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
    def parse_subckts_names_texts(original_text_no_multiline: str) -> Dict[str, str]:

        lines = original_text_no_multiline.splitlines()
        subckts = {}
        inside_subckt = False
        tmp_subckt_text = ''
        subckt_name = ''

        for line in lines:
            if line.startswith('subckt '):
                inside_subckt = True
                subckt_name = line.split(' ')[1]

            elif line.startswith('ends '):
                inside_subckt = False
                tmp_subckt_text += line + '\n'
                if subckt_name:
                    subckts[subckt_name] = tmp_subckt_text
                tmp_subckt_text = ''

            if inside_subckt:
                tmp_subckt_text += line + '\n'

        return subckts

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
    def parse_single_device(line: str, subckts_names: List[str], parent_subckt='') -> Device:
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
        is_subckt = device_model in subckts_names
        if is_subckt:
            device_type = 'SubCircuit'

        if device_model in SpectreNetlistParser.supported_analogLib:
            device_type = 'AnalogLib'

        if device_model in SpectreNetlistParser.supported_modelnames:
            device_type = 'Mosfet'

        if not device_type:
            raise TypeError('Unsupported device')

        device_name = ''
        # if parent_subckt:
        #     device_name += f'{parent_subckt}.'

        if is_subckt:
            device = SubCircuit()
        else:
            device = Device()
        device.model = device_model
        device.name = device_name + split_line[0]
        device.terminals = split_line[1:-2]
        device.type = device_type
        device.parent_subckt = parent_subckt
        return device

    @staticmethod
    def parse_subckts(highest_hierarchy_devices: List[Device], subckts_names_texts: Dict[str, str]) -> List[Device]:
        devices: List[Device] = []
        # subckts_names = list(subckts_names_texts.keys())
        for device in highest_hierarchy_devices:
            if device.model in subckts_names_texts:
                devices.extend(SpectreNetlistParser.parse_subckt('',device.name, device.model,
                                                                 subckts_names_texts))
        return devices

    @staticmethod
    def parse_subckt(parent_subckt: str, instance_name: str, subckt_name: str,
                     subckt_names_texts: Dict[str, str]) -> List[Device]:
        output_devices: List[Device] = []
        subckt_names = list(subckt_names_texts.keys())
        subckt_string = subckt_names_texts[subckt_name]
        splitted_subckt_string = subckt_string.splitlines()
        full_name = f'{parent_subckt}{"." if parent_subckt else ""}{instance_name}'
        for line in splitted_subckt_string[1:-1]:
            parsed_device: Device = SpectreNetlistParser.parse_single_device(line, subckt_names, full_name)
            output_devices.append(parsed_device)

            if parsed_device.type == 'SubCircuit':
                parsed_device: SubCircuit
                parsed_subckt_devices = SpectreNetlistParser.parse_subckt(full_name, parsed_device.name,
                                                                          parsed_device.model, subckt_names_texts)
                parsed_device.devices = parsed_subckt_devices
                output_devices.extend(parsed_subckt_devices)
        return output_devices


if __name__ == '__main__':
    parsed_netlist = SpectreNetlistParser.parse_netlist(
        'D:\\Projects\\SpectreNetlistParser\\Testing_netlists\\divider_new_netlist.scs')
    x = 1
