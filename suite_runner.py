from multiprocessing.pool import ThreadPool
import subprocess
import logging
import re
import time
import argparse
import os
import collections
from lib.src.filepath import FilePath
from lib.src.runner_aggregator import RunnerAggregator
import json
import ConfigParser

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

fp = FilePath()

THIS_DIR = os.path.join(__file__, os.pardir)
LIB_PATH_DIR = os.path.abspath('lib')
LIB_PATH = os.path.abspath('lib'.format(fp.get_filepaths(LIB_PATH_DIR)[3].split('/')[5]))
TEST_PATH_DIR = os.path.abspath(os.path.join(THIS_DIR, 'tests/'))
repo_dir = fp.get_filepaths(TEST_PATH_DIR)[2].split('/')[5]
repo_lib = fp.get_filepaths(LIB_PATH_DIR)[4].split('/')[5]
TEST_PATH = os.path.abspath(os.path.join(THIS_DIR, 'tests/{repo_dir}'
                                         .format(repo_dir=fp.get_filepaths(TEST_PATH_DIR)[2].split('/')[5])))
LIB_CONFIG_PATH = os.path.abspath(os.path.join(THIS_DIR, 'lib/{repo_lib}/config/settings.ini'.format(repo_lib=repo_lib)))
# print LIB_CONFIG_PATH

runner_aggregator = RunnerAggregator()

# for the time being this will return test repo directory


# Traverse Test directory and print out
# available Project, Templates and Tests
def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        try:
            strip_pycache = bool(re.search('__pycache__', dirs[0]))
        except IndexError:
            pass

        if strip_pycache is True:
            try:
                dirs.pop()
            except IndexError:
                pass

        print('\033[1;34m{}{}/\033[1;m'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            strip_init = bool(re.search('init', f))
            strip_cache = bool(re.search('pyc', f))
            if strip_init is False and strip_cache is False:
                print('\033[1;32m{}{}\033[1;m'.format(subindent, f))


parse = argparse.ArgumentParser()
parse.add_argument('--list', help='all, projects, types, templates, suites, tests, browsers')
parse.add_argument('--project')
parse.add_argument('--template')
parse.add_argument('--env', help='options: stage, qa, prod, dev')
parse.add_argument('--test_type', help='browser, api, mobile')
parse.add_argument('--runner', help='options: local, local_X, grid, browserstack, \
                   browserstack_mobile_ios, browserstack_mobile_droid, browserstack_X')
parse.add_argument('--browser', help='enter browser configs here')
parse.add_argument('--test_suite')
parse.add_argument('--single_test')
parse.add_argument('--report_db', help='options: mongodb, jenkins')
args = parse.parse_args()

args_dict = dict(vars(args))

project = args_dict['project']
template = args_dict['template']
test_env = args_dict['env']
runner = args_dict['runner']
test_suite = args_dict['test_suite']
test_type = args_dict['test_type']
show_files = args_dict['list']
single_test = args_dict['single_test']
report_db = args_dict['report_db']
browser_opts = args_dict['browser']

# This prints out available running options in the console
if show_files == 'all':
    print list_files(TEST_PATH)
if show_files == 'projects':
    for i in fp.prj_names():
        print '\033[1;32m{0}\033[1;m'.format(i)
if show_files == 'types':
    for i in fp.test_types():
        print '\033[1;32m{0}\033[1;m'.format(i)
if show_files == 'templates':
    for i in fp.template_names():
        print '\033[1;32m{0}\033[1;m'.format(i)
if show_files == 'suites':
    for i in fp.test_suites():
        print '\033[1;32m{0}\033[1;m'.format(i)
if show_files == 'tests':
    for i in fp.single_test_names():
        print '\033[1;32m{0}\033[1;m'.format(i)
if show_files == 'browsers':
    try:
        for i in runner_aggregator.list_enabled_config_names():
            print '\033[1;32m{0}\033[1;m'.format(i)
    except TypeError:
        pass


threads = 2
ctime = time.strftime('%s')


# Create a .json file after running tests
# and dump user arg test environment and runner
def export_runner_opts():
    test_opts = {'test_env': test_env, 'test_runner': runner, 'test_repo': repo_dir, 'lib_repo': repo_lib}
    with open('runner_opts.json', 'w+') as outfile:
        json.dump(test_opts, outfile)

export_runner_opts()


# Generate an array of absolute paths
# for all test files
def fetch_test_structure():
    actual_tests = []
    fp = FilePath()
    get_test_structure = fp.get_filepaths(TEST_PATH)
    for i in get_test_structure:
        if bool(re.search('init', i)) is False and bool(re.search('pyc', i)) is False:
            actual_tests.append(i)

    return actual_tests


# Generate a list of nested arrays that contain
# an array for browser projects, templates and test suites
# this is generated based on test_type user input
def build_browser_test_suite_config(test_structure):
    test_suite_iter = []
    trim_test_path = []
    project_name = []
    browser_env = []
    browser_suite = []
    for abs_path in test_structure:
        create_dir_arr = abs_path.split('/')
        for iteration in xrange(len(create_dir_arr)):
            if bool(re.search('qaopensource-framework', create_dir_arr[iteration])) is True:
                test_suite_iter.append(iteration)
        filter_project = []
        for num in range(test_suite_iter[0], len(create_dir_arr)):
            filter_project.append(create_dir_arr[num])

        trim_test_path.append(filter_project)
    for iter_trimmed_path in trim_test_path:
        project_name.append(iter_trimmed_path[2])
        if iter_trimmed_path[3] == 'api':
            pass
        elif iter_trimmed_path[3] == 'mobile':
            pass
        elif iter_trimmed_path[3] == 'README.md':
            pass
        elif iter_trimmed_path[3] == '.git':
            pass
        else:
            browser_env.append(iter_trimmed_path[5])
            try:
                browser_suite.append(iter_trimmed_path[6])
            except IndexError:
                pass
    project_name = list(set(project_name))
    browser_env = list(set(browser_env))
    browser_suite = list(set(browser_suite))
    return project_name, browser_env, browser_suite


# Generate a nested list of available browser test type -
# test suites
def send_browser_test_suite_configs():
    config = build_browser_test_suite_config(fetch_test_structure())
    browser_tests = {}
    test_suites = []
    for project_number in xrange(len(config[0])):
        project_number -= 1
        test_suites.append(config[0][project_number])
        browser_tests['browser_project_{0}: '.format(str(project_number+2))] = config[0][project_number]

    for template_number in xrange(len(config[1])):
        browser_tests['browser_template_{0}: '.format(str(template_number+1))] = config[1][template_number]

    for test_suite_number in xrange(len(config[2])):
        browser_tests['browser_test_suite_{0}: '.format(str(test_suite_number+1))] = config[2][test_suite_number]

    sorted_browser_test = collections.OrderedDict(sorted(browser_tests.items()))

    return sorted_browser_test


# Generate a list of nested arrays that contain
# an array for mobile projects, templates and test suites
# this is generated based on test_type user input
def build_mobile_test_suite_config(test_structure):
    test_suite_iter = []
    trim_test_path = []
    project_name = []
    mobile_env = []
    mobile_suite = []
    for abs_path in test_structure:
        create_dir_arr = abs_path.split('/')
        for iteration in xrange(len(create_dir_arr)):
            if bool(re.search('qaopensource-framework', create_dir_arr[iteration])) is True:
                test_suite_iter.append(iteration)
        filter_project = []
        for num in range(test_suite_iter[0], len(create_dir_arr)):
            filter_project.append(create_dir_arr[num])
            trim_test_path.append(filter_project)
    for iter_trimmed_path in trim_test_path:
        project_name.append(iter_trimmed_path[2])
        if iter_trimmed_path[3] == 'api':
            pass
        elif iter_trimmed_path[3] == 'mobile':
            mobile_env.append(iter_trimmed_path[4])
            mobile_suite.append(iter_trimmed_path[5])
    project_name = list(set(project_name))
    mobile_env = list(set(mobile_env))
    mobile_suite = list(set(mobile_suite))
    return project_name, mobile_env, mobile_suite


# Generate a nested list of available mobile test type -
# test suites
def send_mobile_test_suite_configs():
    config = build_mobile_test_suite_config(fetch_test_structure())
    mobile_tests = {}
    test_suites = []
    for project_number in xrange(len(config[0])):
        project_number -= 1
        test_suites.append(config[0][project_number])
        mobile_tests['mobile_project_{0}: '.format(str(project_number+2))] = config[0][project_number]

    for template_number in xrange(len(config[1])):
        mobile_tests['mobile_template_{0}: '.format(str(template_number+1))] = config[1][template_number]

    for test_suite_number in xrange(len(config[2])):
        mobile_tests['mobile_test_suite_{0}: '.format(str(test_suite_number+1))] = config[2][test_suite_number]

    return mobile_tests


# Generate a list of nested arrays that contain
# an array for api projects and test suites
# this is generated based on test_type user input
def build_api_test_suite_config(test_structure):
    test_suite_iter = []
    trim_test_path = []
    project_name = []
    api_suite_names = []
    for abs_path in test_structure:
        create_dir_arr = abs_path.split('/')
        for iteration in xrange(len(create_dir_arr)):
            if bool(re.search('qaopensource-framework', create_dir_arr[iteration])) is True:
                test_suite_iter.append(iteration)
        filter_project = []
        for num in range(test_suite_iter[0], len(create_dir_arr)):
            filter_project.append(create_dir_arr[num])

        trim_test_path.append(filter_project)
    for iter_trimmed_path in trim_test_path:
        project_name.append(iter_trimmed_path[2])
        if iter_trimmed_path[3] == 'api':
            api_suite_names.append(iter_trimmed_path[4])
    project_name = list(set(project_name))
    api_suite_names = list(set(api_suite_names))
    return project_name, api_suite_names


# Generate a nested list of available api test type -
# test suites
def send_api_test_suite_configs():
    config = build_api_test_suite_config(fetch_test_structure())
    api_tests = {}
    test_suites = []
    for project_number in xrange(len(config[0])):
        project_number -= 1
        test_suites.append(config[0][project_number])
        api_tests['api_project_{0}: '.format(str(project_number+2))] = config[0][project_number]

    for test_number in xrange(len(config[1])):
        api_tests['api_test_suite_{0}: '.format(str(test_number+1))] = config[1][test_number]

    sorted_api_test = collections.OrderedDict(sorted(api_tests.items()))

    return sorted_api_test


# Verify user template input with available
# templates. Generate an array with valid templates.
def get_templates(template_name):
    valid_templates = []
    usr_template_in = template.split(',')
    for template_num, template_title in send_browser_test_suite_configs().iteritems():
        for n in usr_template_in:
            check_b = bool(re.search(template_title, template_name))
            check_len = bool(len(template_title) == len(n))
            if check_b and check_len is True:
                valid_templates.append(template_title)

    return valid_templates


# Verify user test suite input with available
# test suites. Generate an array with valid test suites.
def get_suites(usr_input_test_suite_arg):
    suite_arr = []
    if test_type == 'browser':
        for browser_test_suite_num, browser_test_suite_name in send_browser_test_suite_configs().iteritems():
            check_b = bool(re.search(browser_test_suite_name, test_suite))
            if check_b is True and test_suite != 'all':
                suite_arr.append(browser_test_suite_name)
    elif test_type == 'mobile':
        for mobile_test_suite_num, mobile_test_suite_name in send_mobile_test_suite_configs().iteritems():
            check_b = bool(re.search(mobile_test_suite_name, test_suite))
            if check_b is True and test_suite != 'all':
                suite_arr.append(mobile_test_suite_name)
    elif test_type == 'api':
        for api_test_suite_num, api_test_suite_name in send_api_test_suite_configs().iteritems():
            check_b = bool(re.search(api_test_suite_name, test_suite))
            if check_b is True and test_suite != 'all':
                suite_arr.append(api_test_suite_name)

    return suite_arr


# Generate an array of all browser options from user input
def get_runner_opts(runner_opts):
    try:
        usr_runner_opts = browser_opts.split(',')
        return usr_runner_opts
    except:
        pass


# Generate an array with all browser capabilities based on
# browser configs passed through gen_runner_opts
def create_caps_arr():
    caps_arr = []
    for iterate_caps in get_runner_opts(browser_opts):
        caps_arr.append(runner_aggregator.generate_caps_from_config(iterate_caps))
    return caps_arr


# Generate a list of pytest commands to be threaded
def compile_command(proj, env, test_type, runner):
    proc_list = []
    template_name = []
    set_get_suites = set(get_suites(test_suite))

    single_cmd = "py.test tests/{repo_dir}/{project}/{test_type}/{template_title}/{test_suite}/{test_name} " \
                 "--env {template_nm}_{test_env} --runner {test_runner} " \
                 "--json-filename=reports/{datetime}_{template_nm}_{test_env}_report.json " \
                 "--mongodb_report={mongo_bool} {jreport}"

    cmd = "py.test tests/{repo_dir}/{project}/{test_type}/{template_title}/{test_suite}/ " \
          "--env {template_nm}_{test_env} --runner {test_runner} " \
          "--json-filename=reports/{datetime}_{template_nm}_{test_env}_report.json " \
          "--mongodb_report={mongo_bool} {jreport}"

    api_cmd = "py.test tests/{repo_dir}/{project}/{test_type}/{test_suite}/"
    # single api test command not implemented yet
    single_api_cmd = "py.test tests/{repo_dir}/{project}/{test_type}/{test_suite}/{test_name}"

    if test_type == 'browser' or test_type == 'mobile':
        if bool(single_test) is False:
            for template_title in get_templates(template):
                template_name.append(template_title)
                for test_suite_name in set_get_suites:
                    if report_db == 'mongodb':
                        proc_list.append(cmd.format(repo_dir=repo_dir, project=proj, test_type=test_type,
                                                    template_title=template_title, test_suite=test_suite_name,
                                                    test_env=env, test_runner=runner,
                                                    template_nm=template_title.replace('_template', ''),
                                                    datetime=ctime, mongo_bool=True, jreport=''))

                    elif report_db == 'jenkins':
                        jreport = "--junitxml={datetime}_{template_nm}_{test_env}_{test_suite}_report.xml"\
                            .format(test_env=env,
                                    template_nm=template_title.replace('_template', ''),
                                    datetime=ctime, test_suite=test_suite_name)

                        proc_list.append(cmd.format(repo_dir=repo_dir, project=proj, test_type=test_type,
                                                    template_title=template_title, test_suite=test_suite_name,
                                                    test_env=env, test_runner=runner,
                                                    template_nm=template_title.replace('_template', ''),
                                                    datetime=ctime, mongo_bool='', jreport=jreport))
                    else:
                        proc_list.append(cmd.format(repo_dir=repo_dir, project=proj, test_type=test_type,
                                                    template_title=template_title, test_suite=test_suite_name,
                                                    test_env=env, test_runner=runner,
                                                    template_nm=template_title.replace('_template', ''),
                                                    datetime=ctime, mongo_bool='', jreport=''))
        elif bool(single_test) is True:
            for template_title in get_templates(template):
                template_name.append(template_title)
                for test_suite_name in set_get_suites:
                    if report_db == 'mongodb':
                        proc_list.append(single_cmd.format(repo_dir=repo_dir, project=proj, test_type=test_type,
                                                           template_title=template_title, test_suite=test_suite_name,
                                                           test_env=env, test_runner=runner,
                                                           template_nm=template_title.replace('_template', ''),
                                                           datetime=ctime, test_name=single_test,
                                                           mongo_bool=True, jreport=''))
                    elif report_db == 'jenkins':
                        jreport = "--junitxml={datetime}_{template_nm}_{test_env}_{test_suite}_report.xml"\
                            .format(test_env=env,
                                    template_nm=template_title.replace('_template', ''),
                                    datetime=ctime, test_suite=test_suite_name)

                        proc_list.append(single_cmd.format(repo_dir=repo_dir, project=proj, test_type=test_type,
                                                           template_title=template_title, test_suite=test_suite_name,
                                                           test_env=env, test_runner=runner,
                                                           template_nm=template_title.replace('_template', ''),
                                                           datetime=ctime, test_name=single_test,
                                                           mongo_bool='', jreport=jreport))
                    else:
                        proc_list.append(single_cmd.format(repo_dir=repo_dir, project=proj, test_type=test_type,
                                                           template_title=template_title, test_suite=test_suite_name,
                                                           test_env=env, test_runner=runner,
                                                           template_nm=template_title.replace('_template', ''),
                                                           datetime=ctime, test_name=single_test,
                                                           mongo_bool='', jreport=''))
    elif test_type == 'api':
        if bool(single_test) is False:
            for test_suite_name in set_get_suites:
                proc_list.append(api_cmd.format(repo_dir=repo_dir, project=proj, test_type=test_type, test_suite=test_suite_name))
        elif bool(single_test) is True:
            for test_suite_name in set_get_suites:
                proc_list.append(api_cmd.format(repo_dir=repo_dir, project=proj, test_type=test_type,
                                                test_suite=test_suite_name, test_name=single_test))

    return proc_list


def work(item):
    my_tool_subprocess = subprocess.Popen(item.format(test_env, runner), shell=True)
    my_tool_subprocess.wait()

tp = ThreadPool(int(threads))
try:
    if len(get_runner_opts(browser_opts)) > 0 and runner == 'browserstack' or runner == 'browserstack_X':
        create_caps_arr_mod = create_caps_arr()

        while len(create_caps_arr_mod) > 0:
            for number in xrange(len(create_caps_arr())):
                CONFIG_PARSER = ConfigParser.SafeConfigParser()
                CONFIG_PARSER.read(LIB_CONFIG_PATH)

                CONFIG_PARSER.set('browserstack_caps', 'os', create_caps_arr_mod[0]['os'])
                CONFIG_PARSER.set('browserstack_caps', 'platform', str(create_caps_arr_mod[0]['os_version']))
                CONFIG_PARSER.set('browserstack_caps', 'browser', create_caps_arr_mod[0]['browser'])
                CONFIG_PARSER.set('browserstack_caps', 'version', str(create_caps_arr_mod[0]['browser_version']))
                CONFIG_PARSER.set('browserstack_caps', 'resolution', create_caps_arr_mod[0]['resolution'])

                with open(LIB_CONFIG_PATH, 'wb') as configfile:
                    CONFIG_PARSER.write(configfile)

                create_caps_arr_mod.pop(0)

                for commands in compile_command(project, test_env, test_type, runner):
                    print 'Running ' + commands
                    tp = ThreadPool(int(threads))
                    tp.apply_async(work, (commands, ))

                    tp.close()
                    tp.join()

    elif runner == 'local' or runner == 'local_X':
        config_parser = ConfigParser.SafeConfigParser()
        config_parser.read(LIB_CONFIG_PATH)
        config_parser.set('local_settings', 'browser', browser_opts)

        with open(LIB_CONFIG_PATH, 'wb') as configfile:
            config_parser.write(configfile)

        for i in compile_command(project, test_env, test_type, runner):
                print 'Running ' + i
                tp = ThreadPool(int(threads))
                tp.apply_async(work, (i,))

                tp.close()
                tp.join()
    elif runner == 'grid' or runner == 'grid_X':
        config_parser = ConfigParser.SafeConfigParser()
        config_parser.read(LIB_CONFIG_PATH)
        config_parser.set('local_settings', 'browser', browser_opts)

        with open(LIB_CONFIG_PATH, 'wb') as configfile:
            config_parser.write(configfile)

        for i in compile_command(project, test_env, test_type, runner):
                print 'Running ' + i
                tp = ThreadPool(int(threads))
                tp.apply_async(work, (i,))

                tp.close()
                tp.join()
except TypeError:
    pass
