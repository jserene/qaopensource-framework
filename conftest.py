import time
import pytest
from pymongo import MongoClient
from lib.src import configure
from lib.src.test_suite_aggregator import TestSuiteAggregator

settings_parser = configure.read_config()
mongo_url = settings_parser.get('mongodb_settings', 'mongodb_url')

client = MongoClient(mongo_url)

db = client['qaopensource-framework']
reports_collection = db['reports']

report = {
        'passed': [],
        'skipped': [],
        'failed': [],
        'duration': 0.0,
        'total_passed': 0,
        'total_skipped': 0,
        'total_failed': 0,
        'time': 0,
        'test_type': [],
        'template_name': [],
        'test_suite': [],
        'environment': [],
        'project': [],
        'run_id': []
        }

ts = TestSuiteAggregator()

RUNNERS = ('local', 'local_X', 'saucelabs', 'browserstack', 'browserstack_mobile_ios', 'grid', 'grid_X',
           'browserstack_mobile_droid', 'browserstack_X')
ENVIRONMENTS = (ts.collect_environments())


def pytest_addoption(parser):
    """Add additional options to the command line parser."""
    parser.addoption('--env', action='store', dest='env', type='string',
                     choices=ENVIRONMENTS,
                     help='Environment in which to run tests.')

    parser.addoption('--runner', action='store', dest='runner', type='string',
                     choices=RUNNERS, default='browserstack',
                     help='The remote or local runner that will handle the Selenium instances.')

    group = parser.getgroup("dump_to_json")
    group.addoption("--json-filename", action="store", help='The json filename to which to dump test results.')

    group = parser.getgroup("mongo_reports")
    group.addoption("--mongodb_report", action="store", required=False, default=False)


def generate_run_ids(get_time):
    tmp = []
    tmp.append(get_time)
    return tmp[0]


def pytest_runtest_makereport(item, call, __multicall__):
    rep = __multicall__.execute()
    report['duration'] += rep.duration
    report['time'] = time.ctime()
    report['project'].append(None)
    report['project'][0] = rep.nodeid.split('/')[1]
    report['test_type'].append(rep.nodeid.split('/')[2])
    report['template_name'].append(rep.nodeid.split('/')[3])
    report['test_suite'].append(rep.nodeid.split('/')[4])
    env_url = settings_parser.get('url', 'base_url')

    report['environment'].append(env_url)

    get_time_for_id = generate_run_ids(time.strftime('%H%w'))

    report['run_id'].append(get_time_for_id)

    if rep.when == "call":
        if rep.passed:
            report['passed'].append(rep.nodeid.split('::')[-1])
            report['total_passed'] += 1

        if rep.failed:
            report['failed'].append(rep.nodeid.split('::')[-1])
            report['total_failed'] += 1
    else:
        if rep.skipped:
            report['skipped'].append(rep.nodeid)
            report['total_skipped'] += 1

    return rep


def pytest_configure(config):
    pass


def pytest_sessionfinish(session, exitstatus):
    if report['passed'] or report['failed'] or report['skipped']:
        filename = session.config.getoption('--json-filename')
        #jdump = json.dumps(report, sort_keys=True, indent=4, separators=(',', ': '))
        if bool(session.config.getoption('--mongodb_report')) is True:
            insert_report = reports_collection.insert_one(report)

        #json.dumps(report, reports_collection.insert_one(report).inserted_id, sort_keys=True, indent=4, separators=(',', ': '))
        # with open(filename, 'w') as f:
        #     json.dump(report, f, sort_keys=True, indent=4, separators=(',', ': '))


@pytest.fixture(scope='session', autouse=True)
def config(request):
    env = request.config.getvalue('env')
    runner = request.config.getvalue('runner')
    _config = configure.read_config()
    if env and runner:
        configure.update_config(_config, env, runner)

    return _config
