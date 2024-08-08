from Netlist import Netlist


class SpectreNetlistParser:
    supported_analogLib = ['vsource', 'resistor', 'vcvs', 'cvcs', 'cccs', 'ccvs', 'capacitor', 'transformer']
    supported_modelnames = ['nch', 'pch', 'nch_lvt', 'pch_lvt']
    supported_commands = ['tran', 'dc', 'ac', 'info', 'noise', 'xf', 'pss']

    @staticmethod
    def parse_netlist(path: str):
        output_netlist = Netlist(path)
        output_netlist.subckts_names = SpectreNetlistParser.parse_subckts(output_netlist)
        return output_netlist

    @staticmethod
    def parse_subckts(netlist: Netlist):
        original_string = netlist.original_string
        if not original_string:
            raise ValueError

        subckt_names = []
        inside_subckt = False
        lines = original_string.splitlines()

        for idx, line in enumerate(lines):
            if line.startswith('subckt '):
                inside_subckt = True
                subckt_name = line.split(' ')[1]
                subckt_names.append(subckt_name)

            elif line.startswith('ends'):
                inside_subckt = False

        return subckt_names


if __name__ == '__main__':
    parsed_netlist = SpectreNetlistParser.parse_netlist(
        'D:\\Projects\\SpectreNetlistParser\\Testing_netlists\\divider_new_netlist.scs')
    x = 1