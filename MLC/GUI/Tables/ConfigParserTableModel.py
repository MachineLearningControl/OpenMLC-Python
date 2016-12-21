from MLC.GUI.Tables.ConfigTableModel import ConfigTableModel


class ConfigParserTableModel(ConfigTableModel):

    def __init__(self, name, config_parser, header, parent=None, *args):
        adapted_data = self._config_parser_to_list_of_lists(config_parser)
        ConfigTableModel.__init__(self, name, adapted_data, header, parent, *args)

    def _config_parser_to_list_of_lists(self, config_parser):
        data = []
        for each_section in config_parser.sections():
            for (each_key, each_val) in config_parser.items(each_section):
                data.append([each_key, each_section, each_val])
        return data
