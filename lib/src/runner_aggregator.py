import os
import json
from filepath import FilePath
import re

THIS_DIR = os.path.join(__file__, os.pardir)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.abspath(os.path.join(ROOT_DIR, '../../'))


def suite_runner_test_repo():
    with open('{root_path}/runner_opts.json'.format(root_path=ROOT_PATH)) as data_file:
        runner_data = json.load(data_file)
        return runner_data['test_repo']


def suite_runner_lib_repo():
    with open('{root_path}/runner_opts.json'.format(root_path=ROOT_PATH)) as data_file:
        runner_data = json.load(data_file)
        return runner_data['lib_repo']

LIB_PATH = os.path.abspath(os.path.join(THIS_DIR, os.pardir))
TEST_PATH = os.path.abspath(os.path.join(THIS_DIR, '../../tests/{repo_dir}/'.format(repo_dir=suite_runner_test_repo())))


class RunnerAggregator(object):

    def fetch_runner_configs(self):
        fp = FilePath()
        get_structure = fp.get_filepaths('{lib_path}/{lib_repo}/config/runners'
                                         .format(lib_path=LIB_PATH, lib_repo=suite_runner_lib_repo()))

        return get_structure

    def build_runner_config_json(self, files):
        agg_env = []
        for iter_configs in files:
            with open(iter_configs) as data_file:
                data = json.load(data_file)
                agg_env.append(data)
        return agg_env

    def send_runner_configs(self):
        return self.build_runner_config_json(self.fetch_runner_configs())

    def capture_enabled(self):
        enabled_configs = []
        capture_configs = self.send_runner_configs()
        for iter_enabled_config in xrange(len(capture_configs)):
            for runner_config_key, runner_config_value in capture_configs[iter_enabled_config].iteritems():
                if runner_config_key == 'enabled' and runner_config_value == 'true':
                    enabled_configs.append(capture_configs[iter_enabled_config])
        return enabled_configs

    def suite_runner_opts(self):
        with open('{root_path}/runner_opts.json'.format(root_path=ROOT_PATH)) as data_file:
            runner_data = json.load(data_file)
            return runner_data['test_runner']

    def collect_configs_by_opts(self, runner):
        enabled_configs = self.capture_enabled()
        enabled_browserstack_configs = []
        enabled_local_configs = []
        if runner == 'browserstack' or runner == 'browserstack_X':
            for iter_enabled_configs in xrange(len(enabled_configs)):
                for runner_config_key, runner_config_value in enabled_configs[iter_enabled_configs].iteritems():
                    if runner_config_key == 'runner' and \
                                    runner_config_value == 'browserstack' or runner_config_value == 'browserstack_X':
                        enabled_browserstack_configs.append(enabled_configs[iter_enabled_configs])
            return enabled_browserstack_configs
        if runner == 'local' or runner == 'local_X':
            for iter_enabled_configs in xrange(len(enabled_configs)):
                for runner_config_key, runner_config_value in enabled_configs[iter_enabled_configs].iteritems():
                    if runner_config_key == 'runner' and runner_config_value == 'local':
                        enabled_local_configs.append(enabled_configs[iter_enabled_configs])
        if runner == 'grid' or runner == 'grid_X':
            for iter_enabled_configs in xrange(len(enabled_configs)):
                for runner_config_key, runner_config_value in enabled_configs[iter_enabled_configs].iteritems():
                    if runner_config_key == 'runner' and runner_config_value == 'grid':
                        enabled_local_configs.append(enabled_configs[iter_enabled_configs])

            return enabled_local_configs

    def send_update_config(self):
        if self.suite_runner_opts() is None:
            return self.collect_configs_by_opts('browserstack')
        else:
            return self.collect_configs_by_opts(self.suite_runner_opts())

    def list_enabled_config_names(self):
        enabled_configs = self.send_update_config()
        config_names = []
        for iter_enabled_configs in xrange(len(enabled_configs)):
            for runner_config_key, runner_config_value in enabled_configs[iter_enabled_configs].iteritems():
                if runner_config_key == 'name':
                    config_names.append(runner_config_value)

        return config_names

    def generate_caps_from_config(self, config_name):
        ver_dict = {}
        enabled_configs = self.send_update_config()
        for iter_enabled_configs in xrange(len(enabled_configs)):
            for caps_key, caps_value in enabled_configs[iter_enabled_configs].iteritems():
                if caps_key == 'name' and bool(re.search(config_name, caps_value)):
                    ver_dict['os'] = enabled_configs[iter_enabled_configs]['os']
                    ver_dict['os_version'] = enabled_configs[iter_enabled_configs]['platform']
                    ver_dict['browser'] = enabled_configs[iter_enabled_configs]['browser']
                    ver_dict['browser_version'] = enabled_configs[iter_enabled_configs]['version']
                    ver_dict['resolution'] = enabled_configs[iter_enabled_configs]['resolution']
                    ver_dict['browserstack.debug'] = True
                    ver_dict['browserstack.video'] = enabled_configs[iter_enabled_configs]['video']

        return ver_dict
