import os, unittest
from MLC.mlc_parameters.mlc_parameters import Config


class ConfigTest(unittest.TestCase):
    TEST_FILENAME = "test_mlc_parameters_tmp_file.ini"

    def setUp(self):
        test_file = """[SECTION_NUMBERS]
int_field=1
float_field=0.004
[SECTION_BOOLEANS]
bool_field_true=true
bool_field_false=false
[SECTION_LISTS]
list_int_field = 1,5,10,15
list_float_field = 1.01,5.05
list_string_field = 1,2,3
list_range = 1:10
list_float_range = 1:10"""

        with open(ConfigTest.TEST_FILENAME, 'w+') as f:
            f.write(test_file)

        self._config = Config().get_instance()
        self._config.read(ConfigTest.TEST_FILENAME)

    def tearDown(self):
        os.remove(ConfigTest.TEST_FILENAME)

    def test_config_numbers(self):
        value = self._config.getint("SECTION_NUMBERS", "int_field")
        self.assertEqual(value, 1)
        self.assertTrue(isinstance(value, int))

        value = self._config.getfloat("SECTION_NUMBERS", "float_field")
        self.assertEqual(value, 0.004)
        self.assertTrue(isinstance(value, float))

    def test_config_booleans(self):
        value = self._config.getboolean("SECTION_BOOLEANS", "bool_field_true")
        self.assertTrue(value)
        self.assertTrue(isinstance(value, bool))

        value = self._config.getboolean("SECTION_BOOLEANS", "bool_field_false")
        self.assertFalse(value)
        self.assertTrue(isinstance(value, bool))

    def test_config_lists(self):
        value = self._config.get_list("SECTION_LISTS", "list_int_field")
        self.assertEquals(value, [1, 5, 10, 15])
        self.assertTrue(isinstance(value, list))

        value = self._config.get_list("SECTION_LISTS", "list_float_field", item_type=float)
        self.assertEquals(value, [1.01, 5.05])
        self.assertTrue(isinstance(value, list))

        value = self._config.get_list("SECTION_LISTS", "list_string_field", item_type=str)
        self.assertEquals(value, ["1", "2", "3"])
        self.assertTrue(isinstance(value, list))

        value = self._config.get_list("SECTION_LISTS", "list_range")
        self.assertEquals(value, range(1, 10))
        self.assertTrue(isinstance(value, list))

        value = self._config.get_list("SECTION_LISTS", "list_float_range", item_type=float)
        self.assertEquals(value, [float(x) for x in range(1, 10)])

        for item in value:
            self.assertTrue(isinstance(item, float))
        self.assertTrue(isinstance(value, list))

