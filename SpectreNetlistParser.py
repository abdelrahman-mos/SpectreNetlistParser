from typing import List, Dict
from Netlist import Netlist


class SpectreNetlistParser:
    supported_analogLib = ['vsource', 'resistor', 'vcvs', 'cvcs', 'cccs', 'ccvs', 'capacitor', 'transformer']
    supported_modelnames = ['nch', 'pch', 'nch_lvt', 'pch_lvt']
    supported_commands = ['tran', 'dc', 'ac', 'info', 'noise', 'xf', 'pss', 'options', 'parameters', 'global',
                          'simulator']

    @staticmethod
    def parse_netlist(path: str):
        output_netlist = Netlist(path)
        original_text = output_netlist.original_string
        original_text_no_comments = SpectreNetlistParser.remove_comments(original_text)
        subckts_names = SpectreNetlistParser.parse_subckts(original_text_no_comments)
        original_text_no_subckts = SpectreNetlistParser.remove_subckts(original_text_no_comments)
        original_text_no_commands = SpectreNetlistParser.remove_commands(original_text_no_subckts)
        highest_hierarchy_devices = SpectreNetlistParser.parse_highest_hierarchy(original_text_no_commands, subckts_names)
        output_netlist.subckts_names = subckts_names
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
    def parse_subckts(original_text_no_comments: str) -> List[str]:

        subckt_names = []
        inside_subckt = False
        lines = original_text_no_comments.splitlines()

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
    def remove_commands(original_text_no_subckts: str) -> str:
        output_text = ''
        return output_text

    @staticmethod
    def parse_highest_hierarchy(original_text_no_subckts: str, subckts_names: List[str]) -> Dict[str, Dict]:
        pass


if __name__ == '__main__':
    parsed_netlist = SpectreNetlistParser.parse_netlist(
        'D:\\Projects\\SpectreNetlistParser\\Testing_netlists\\divider_new_netlist.scs')
    x = 1
