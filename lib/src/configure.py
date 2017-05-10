#!/usr/bin/env python
import os
import ConfigParser
from lib.src.test_suite_aggregator import TestSuiteAggregator
from lib.src.runner_aggregator import suite_runner_lib_repo

THIS_DIR = os.path.join(__file__, os.pardir)
CONFIG_PATH = os.path.abspath(os.path.join(THIS_DIR, '../{lib_repo}/config/settings.ini'
                                           .format(lib_repo=suite_runner_lib_repo())))
LIB_PATH = os.path.abspath(os.path.join(THIS_DIR, os.pardir))

CONFIG_PARSER = ConfigParser.SafeConfigParser()


def read_config():
    # Reloads the config data loaded into the CONFIG_PARSER
    CONFIG_PARSER.read(CONFIG_PATH)
    return CONFIG_PARSER


CONFIG_PARSER.read(CONFIG_PATH)

ts = TestSuiteAggregator()

SETTINGS = ts.send_env_configs()


def update_config(config, env, runner):
    config.set('location', 'location', runner)
    settings = SETTINGS[env]
    for section, data in settings.iteritems():
        for key, value in data.iteritems():
            config.set(section, key, value)

    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)
