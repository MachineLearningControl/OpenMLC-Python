from mlc import MLC
import requests
import json

import argparse

class MLCClient(MLC):
    def __init__(self, hostname, port):
        self._hostname = hostname
        self._port = port
        self._url = "http://"+hostname+":"+str(port)

    def open_experiment(self, experiment_name):
        raise NotImplementedError("MLC::open_experiment not implemented")

    def close_experiment(self, experiment_name):
        raise NotImplementedError("MLC::close_experiment not implemented")

    def get_workspace_experiments(self):
        response = requests.get(self._url+"/mlc/workspace/experiments")
        return json.loads(response.text)

    def delete_experiment_from_workspace(self, experiment_name):
        response = requests.delete(self._url + "/mlc/workspace/experiments/%s" % experiment_name)
        return json.loads(response.text)

    def new_experiment(self, experiment_name, experiment_configuration):
        json_config = json.dumps(experiment_configuration)
        response = requests.post(self._url+"/mlc/workspace/experiments/%s" % experiment_name, json=json_config)
        return json.loads(response.text)

    def get_experiment_configuration(self, experiment_name):
        raise NotImplementedError("MLC::get_experiment_configuration not implemented")

    def set_experiment_configuration(self, experiment_name, configuration):
        raise NotImplementedError("MLC::set_experiment_configuration not implemented")

    def go(self, experiment_name, to_generation, from_generation=0):
        raise NotImplementedError("MLC::go not implemented")

    def get_experiment_info(self, experiment_name):
        raise NotImplementedError("MLC::get_experiment_info not implemented")

    def get_generation(self, experiment_name, generation_number):
        raise NotImplementedError("MLC::get_generation not implemented")

    def get_individuals(self, experiment_name):
        raise NotImplementedError("MLC::get_individuals not implemented")


def parse_arguments():
    parser = argparse.ArgumentParser(description='MLC Server (API REST)')

    parser.add_argument('-s', '--mlc-server-hostname', default="127.0.0.1",
                        type=str, help='MLC server hostname.')

    parser.add_argument('-p', '--mlc-server-port', default=5000,
                        type=int, help='MLC Server listening port.')

    return parser.parse_args()


if __name__ == '__main__':
    arguments = parse_arguments()

    print "Connecting with the mlc server at http://%s:%s" % (arguments.mlc_server_hostname, arguments.mlc_server_port)

    first_experiment_name = "first_experiment"
    second_experiment_name = "second_experiment"

    mlc_client = MLCClient(arguments.mlc_server_hostname, arguments.mlc_server_port)

    print "Remember to remove all files in the workspace before running this POC!!!!"

    print "Experiments in the workspace: %s" % mlc_client.get_workspace_experiments()

    print "Add experiment '%s' to the workspace" % first_experiment_name
    experiment_name = "first_experiment_name"
    experiment_configuration = {"POPULATION":
                                    {"size": "100",
                                     "sensors": "1",
                                     "sensor_spec": "false",
                                     "sensor_list": "1, 5, 2, 4"}
                                }

    print mlc_client.new_experiment(first_experiment_name, experiment_configuration)

    print "Experiments in the workspace: %s" % mlc_client.get_workspace_experiments()

    print "Try to create another experiment with the same name must fail"
    print mlc_client.new_experiment(first_experiment_name, experiment_configuration)

    print "Experiments in the workspace: %s" % mlc_client.get_workspace_experiments()

    print "Add experiment %s to the workspace" % second_experiment_name
    print mlc_client.new_experiment(second_experiment_name, experiment_configuration)

    print "Experiments in the workspace: %s" % mlc_client.get_workspace_experiments()

    print "Delete Experiment %s" % second_experiment_name
    print mlc_client.delete_experiment_from_workspace(second_experiment_name)

    print "Experiments in the workspace: %s" % mlc_client.get_workspace_experiments()

    print "Remember to remove all files in the workspace before running this POC!!!!"