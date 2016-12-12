from MLC.GUI.Tables.ConfigTableModel import ConfigTableModel


class ConfigDictTableModel(ConfigTableModel):

    def __init__(self, dict, header, parent=None, *args):
        adapted_data = self._dict_to_list_of_lists(dict)
        ConfigTableModel.__init__(self, adapted_data, header, parent, *args)

    def _dict_to_list_of_lists(self, dict):
        data = []
        for section, options in dict.iteritems():
            for option, value in options.iteritems():
                data.append([option, section, value])
        return data