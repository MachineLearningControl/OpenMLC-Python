#!flask/bin/python
from flask import Flask, jsonify
from flask import make_response
from flask import request

import json
import argparse

from mlc import MLCLocal
from mlc import DuplicatedExperimentError, ExperimentNotExistException

mlc_api = None
app = Flask(__name__)

"""
    POC for workspace methods
"""


@app.route('/mlc/workspace/experiments', methods=['GET'])
def get_workspace_experiments():
    print "Receive request, return workspace experiment names"
    return jsonify(mlc_api.get_workspace_experiments())

@app.route('/mlc/workspace/experiments/<string:experiment_name>', methods=['POST'])
def new_experiment(experiment_name):
    experiment_configuration = json.loads(request.json)

    try:
        print "Receive request, trying to create experiment %s" % experiment_name
        mlc_api.new_experiment(experiment_name, experiment_configuration)

    except DuplicatedExperimentError, err:
        return make_response(jsonify({'error': str(err)}), 409)

    except Exception, err:
        return make_response(jsonify({'error': str(err)}), 500)

    return jsonify("Experiment %s created" % experiment_name)


@app.route('/mlc/workspace/experiments/<string:experiment_name>', methods=['DELETE'])
def delete_experiment_from_workspace(experiment_name):
    try:
        print "Receive request, trying to delete experiment %s" % experiment_name
        mlc_api.delete_experiment_from_workspace(experiment_name)

    except ExperimentNotExistException, err:
        return make_response(jsonify({'error': str(err)}), 409)

    except Exception, err:
        return make_response(jsonify({'error': str(err)}), 500)

    return jsonify("Experiment %s deleted" % experiment_name)


"""
    Not Implemented Yet
"""


def open_experiment(self, experiment_name):
    raise NotImplementedError("MLC::open_experiment not implemented")


def close_experiment(self, experiment_name):
    raise NotImplementedError("MLC::close_experiment not implemented")


def get_experiment_configuration(self, experiment_name):
    raise NotImplementedError("MLC::get_experiment_configuration not implemented")


def set_experiment_configuration(self, experiment_name, configuration):
    raise NotImplementedError("MLC::set_experiment_configuration not implemented")


def go(self, experiment_name, to_generation, from_generation=1):
    raise NotImplementedError("MLC::go not implemented")


def get_experiment_info(self, experiment_name):
    raise NotImplementedError("MLC::get_experiment_info not implemented")


def get_generation(self, experiment_name, generation_number):
    raise NotImplementedError("MLC::get_generation not implemented")


def get_individuals(self, experiment_name):
    raise NotImplementedError("MLC::get_individuals not implemented")


def parse_arguments():
    parser = argparse.ArgumentParser(description='MLC Server (API REST)')

    parser.add_argument('-d', '--workspace-dir', required=True,
                        type=str, help='MLC Workspace directory.')

    parser.add_argument('-p', '--listening-port', default=5000,
                        type=int, help='MLC Server listening port.')

    return parser.parse_args()

if __name__ == '__main__':
    arguments = parse_arguments()
    mlc_api = MLCLocal(arguments.workspace_dir)

    print "Running MLC Server..."
    print "MLC Workspace: %s" % arguments.workspace_dir
    print "MLC Server Listening on 127.0.0.1:%s" % arguments.listening_port

    app.run(port=arguments.listening_port, debug=True)