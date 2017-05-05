---
# QA OpenSource Framework

##### Installation

Linux:
```sh
apt-get install chromedriver libmysqlclient-dev python-pymysql python-mysqldb ffmpeg mongodb mongodb-clients mongodb-server
```

Install Python requirements:
```sh
pip install -r requirements.txt
```

To enable local Firefox testing, [geckodriver](https://github.com/mozilla/geckodriver/releases) is required.
Place `geckodriver` in the same path as the Firefox binary.

##### Browserstack Tunnel

For some of the tests to pass, a browserstack tunnel needs to be created.
The binary can be found [here](https://www.browserstack.com/local-testing).

Example of binary use with tests:

```sh
./BrowserStackLocal --key {browserstack_api_key} --folder /home/User/qaopensource-framework/lib/test_data/project
```
Folder argument points to the `test_data` directory. This allows browserstack to
use local files during test runs.

Example of binary use when testing against localhost:

```sh
./BrowserStackLocal --key {browserstack_api_key} --force-local
```
Note: While using a forced local connection with Browserstack. Test times are extremely slow
since tests will be using your machines connection speeds through a vpn tunnel.

#### Running:

##### Browser Tests:

**Running with suite_runner.py (preferred):**

```sh
$ python suite_runner.py -h
usage: suite_runner.py [-h] [--list LIST] [--project PROJECT]
                       [--template TEMPLATE] [--env ENV]
                       [--test_type TEST_TYPE] [--runner RUNNER]
                       [--browser BROWSER] [--test_suite TEST_SUITE]
                       [--single_test SINGLE_TEST] [--report_db REPORT_DB]

optional arguments:
  -h, --help            show this help message and exit
  --list LIST           all, projects, types, templates, suites, tests,
                        browsers
  --project PROJECT
  --template TEMPLATE
  --env ENV             options: stage, qa, prod, dev
  --test_type TEST_TYPE
                        browser, api, mobile
  --runner RUNNER       options: local, local_X, grid, browserstack,
                        browserstack_mobile_ios, browserstack_mobile_droid,
                        browserstack_X
  --browser BROWSER     enter browser configs here
  --test_suite TEST_SUITE
  --single_test SINGLE_TEST
  --report_db REPORT_DB
                        options: mongodb, jenkins

```
**Browserstack Test Example:**

```sh
$ python suite_runner.py --project=project_1 --template=template_1,template_2 --env=qa --test_type=browser --runner=browserstack --browser=chrome_55,chrome_54 --test_suite=Test_Suite_1 --report_db=mongodb
```

**Local Test Example:**

```sh
$ python suite_runner.py --project=project_1 --template=template_1,template_2 --env=qa --test_type=browser --runner=local --browser=chrome --test_suite=Test_Suite_1 --report_db=mongodb
```
When running locally, specify which local browser you would like to run against.

**API Test Example:**

```sh
$ python suite_runner.py --project=project_1 --template=template_1 --env=qa --test_type=api --runner=local --test_suite=Test_Suite_1
```
API tests can be run against any template.

**Running a single test:**

```sh
$ python suite_runner.py --project=project_1 --template=template_1,template_2 --env=stage --test_type=browser --runner=browserstack --browser=chrome_55,chrome_54 --test_suite=Test_Suite_1 --single_test=test_foo.py --report_db=mongodb
```

You can also run a single test across multiple templates.

```sh
$ python suite_runner.py --project=project_1 --template=template_1,template_2 --env=stage --test_type=browser --runner=browserstack --test_suite=Test_Suite_1 --single=test_foo.py
```

**Running tests with multiple instances of webdriver**

```sh
python suite_runner.py --project=project_1 --template=template_1 --env=dev --test_type=browser --runner=local_X --browser=chrome --test_suite=Test_Suite_1 --single_test=test_foo.py --report_db=mongodb
```
`local_X` will allow the use of 2 webdriver instances locally.
`browserstack_X` will trigger two webdriver instances against browserstack services.
When this option is selected and a test is executed the tests will go into a queue
waiting for any tests or queues in progress to finish before launching tests.


**Get a list of available projects, templates, test suites and test cases options:**

```sh
$ python suite_runner.py --list=all
```

**Get list of enabled browser configs:**

```sh
$ python suite_runner.py --list=browsers
chrome_54
chrome_44
chrome_55
firefox_51
```

**Get list of all current projects:**

```sh
$ python suite_runner.py --list=projects
```

**Get list of all current test types:**

```sh
$ python suite_runner.py --list=types   
mobile
browser
api
```

**Get list of all current project templates:**

```sh
$ python suite_runner.py --list=templates
```

**Get list of available test suites:**

```sh
$ python suite_runner.py --list=suites
```

**Get list of all single test files:**

```sh
$ python suite_runner.py --list=tests
```

#### Directory Structure:

**Tests**

```
tests/project_1/
               /api/
               /browser/
               /mobile/ <--- Test Type
                      /template_1/
                                 /test_suite_1/
                                              /tests_for_suite_1

```
New projects, templates, test suites will automatically be detected.

**Environment Configs**

```
lib/config/environments/
                       /dev/
                       /prod/
                       /qa/
                       /stage/
                             /example_template.json
```

example_template.json:
```json
{
	"example_stage": {
		"url": {
			"base_url": "https://example.com"
		},
		"db_test_settings": {
			"db_name": "example",
			"db_hostname": "db.example.com",
			"db_port": "3306",
			"db_password": "my_password",
			"db_user": "my_user"
		}
	}
}
```

If using mongodb as a data source the template can look like the following:
```json
{
	"example_dev": {
		"url": {
			"base_url": "http://example.com"
		},
		"db_test_settings": {
			"db_name": "none",
			"db_hostname": "host.com",
			"db_port": "mongo_port",
			"db_password": "none",
			"db_user": "none"
		}
	}
}
```

It is important to note, that the first key in the json file must correlate with
the environment you wish to run against. `example_qa` `example_stage` etc.

Also, in this case `example` must have a parent test template `../browser/example_template/..`.

**Runner Configs**

```
lib/config/runners/
                       /grid/
                       /local/
                       /browserstack/
                             /chrome_55.json
```
Browserstack runner example chrome_55.json:

```json
{
  "name": "chrome_55",
  "runner": "browserstack",
  "enabled": "true",
  "os": "Windows",
  "platform": 7,
  "browser": "Chrome",
  "version": 55,
  "resolution": "1920x1080",
  "video": "true"
}
```
The suite runner will only list `enabled` browserstack capabilities.

Browserstack capabilities list can be found [here](https://www.browserstack.com/list-of-browsers-and-platforms?product=automate)

Local runner example chrome.json:
```json
{
	"runner": "local",
	"enabled": "true",
	"browser": "chrome"
}
```

Grid runner example chrome.json:
```json
{
	"runner": "grid",
	"enabled": "true",
	"browser": "chrome"
}
```

##### Runner Options:

`local` Will run tests using the browser on your machine.

`local_X` Will run tests using the browser on your machine. However, this enables multiple
driver instances.

`grid` Will run tests against available selenium grid instances.

`saucelabs` Tests will run remotely against a Saucelabs environment.

`browserstack` Tests will run remotely against a Browserstack environment.

`browserstack_X` Tests will run remotely against a Browserstack environment. However, this
enables multiple driver instances.

`browserstack_mobile_ios` Tests will run through browserstack ios emulator.

`browserstack_mobile_droid` Tests will run through browserstack android emulator.



#### Settings.ini

```ini
[grid]
grid_ip = 192.168.2.133
browser = firefox
```

These are Selenium Grid configurations.
Enter the browser type and IP address of the selenium Hub machine here.


```ini
[sauce_api]
username = saucelabs_username
key = saucelabs_api_key

[browserstack_api]
username = browserstack_username
key = browserstack_api_key
```

Credentials for external services.

#### Reporting

If you would like persistent test results, there is an option to use `mongodb`.
All that is required is a running instance of MongoDB. The mongo connect url can be found
in `settings.ini`, for now. The framework will create a `qaopensource-framework` DB with
a `reports` collection. Each test run will create a document within that collection.

An example of a test run using MongoDB:

```sh
$ python suite_runner.py --project=project_1 --template=template_1 --env=stage --test_type=browser --runner=local --test_suite=Test_Suite_1 --report_db=mongodb
```