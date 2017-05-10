import os
import json
from filepath import FilePath
import re
from runner_aggregator import suite_runner_lib_repo
from runner_aggregator import suite_runner_test_repo

THIS_DIR = os.path.join(__file__, os.pardir)
LIB_PATH = os.path.abspath(os.path.join(THIS_DIR, os.pardir))
TEST_PATH = os.path.abspath(os.path.join(THIS_DIR, '../../tests/{test_rep}/'.format(test_rep=suite_runner_test_repo())))


class TestSuiteAggregator(object):

    def fetch_env_configs(self):
        fp = FilePath()
        get_structure = fp.get_filepaths('{lib_path}/{lib_repo}/config/environments'.format(lib_path=LIB_PATH,
                                                                                            lib_repo=suite_runner_lib_repo()))

        return get_structure

    def build_env_config_json(self, files):
        agg_env = {}
        for iter_env_configs in files:
            with open(iter_env_configs) as data_file:
                data = json.load(data_file)
                if bool(re.search('example', iter_env_configs)) is False:
                    agg_env.update(data)

        return agg_env

    def send_env_configs(self):
        return self.build_env_config_json(self.fetch_env_configs())

    def collect_environments(self):
        env_names = []
        for env_config_key, env_config_value in self.send_env_configs().iteritems():
            env_names.append(env_config_key)

        extract_arr = ', '.join([str(x) for x in env_names])

        return extract_arr
