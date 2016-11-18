from flask import Flask, jsonify
from flask import make_response
from flask import request

import sys
import json
import argparse
import logging

from mlc import MLCLocal
from mlc import DuplicatedExperimentError, ExperimentNotExistException

logger = None
mlc_api = None
app = Flask(__name__)


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

def get_experiment_info(self, experiment_name):
    raise NotImplementedError("MLC::get_experiment_info not implemented")

def go(self, experiment_name, to_generation, from_generation=1):
    raise NotImplementedError("MLC::go not implemented")



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


def get_generation(self, experiment_name, generation_number):
    raise NotImplementedError("MLC::get_generation not implemented")


def get_individuals(self, experiment_name):
    raise NotImplementedError("MLC::get_individuals not implemented")


def parse_arguments():
    log_levels = {
        "ERROR":    logging.ERROR,
        "WARNING":  logging.WARNING,
        "INFO":     logging.INFO,
        "DEBUG":    logging.DEBUG
    }

    parser = argparse.ArgumentParser(description='MLC Server (API REST)')

    parser.add_argument('-w', '--workspace-dir', required=True,
                        type=str, help='MLC Workspace directory.')

    parser.add_argument('-p', '--listening-port', default=5000,
                        type=int, help='MLC Server listening port.')

    parser.add_argument('-s', '--server-hostname', default="127.0.0.1",
                        type=str, help='MLC Server hostname.')

    parser.add_argument('-l', '--log-level', default="INFO",
                        choices=log_levels.keys(), type=str,
                        help='MLC Server logging level.')

    parser.add_argument('--server-debug', action='store_true',
                        help='If the debug flag is set the server'
                             'will automatically reload for code change.')

    arguments = parser.parse_args()
    arguments.log_level = log_levels[arguments.log_level]
    return arguments


def get_app_logger(level):
    app_logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    app_logger.addHandler(handler)
    return app_logger

if __name__ == '__main__':
    # parse mlc_server arguments
    arguments = parse_arguments()

    # set global logging configuration
    logger = get_app_logger(arguments.log_level)

    # instatiate MLCLocal
    logger.info("loading MLC workspace from %s" % arguments.workspace_dir)
    mlc_api = MLCLocal(arguments.workspace_dir)

    # Launch MLC Server
    logger.info("starting MLC Server...")
    logger.info("MLC Server listening on http://%s:%d" % (arguments.server_hostname,
                                                          arguments.listening_port))

    app.run(host=arguments.server_hostname,
            port=arguments.listening_port,
            debug=arguments.server_debug)