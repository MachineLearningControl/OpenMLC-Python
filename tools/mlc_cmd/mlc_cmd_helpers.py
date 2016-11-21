import ConfigParser
from MLC.mlc_parameters.mlc_parameters import Config


def validate_params(param_types, err_handler, fail_message=""):
    def decorator(func):
        def real_decorator(*args, **kwargs):
            self, line = args
            input_values = line.split()

            if len(input_values) > len(param_types):
                print "Bad command arguments, %s" % fail_message
                return False

            input_values = input_values + [None]*(len(param_types) - len(input_values))
            validated_values = None

            try:
                type_values = zip(param_types, input_values)
                validated_values = [t(v) for t, v in type_values]
            except Exception, err:
                print "Bad command arguments, %s" % fail_message
                return False

            try:
                return func(self, *validated_values)
            except Exception, err:
                err_handler(err)

        return real_decorator
    return decorator


def string(value):
    if value is None:
        raise ValueError("null_value, expected string_value")
    return str(value)


def optional(value_type):
    def validate(value):
        if value is not None:
            return value_type(value)
    return validate


def load_configuration(configuration_file):
    config_parser = ConfigParser.ConfigParser()
    config_parser.read(configuration_file)
    return Config.to_dictionary(config_parser)
