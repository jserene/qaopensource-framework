import time
import unittest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from lib.src import configure

settings_parser = configure.read_config()
stack_username = settings_parser.get('browserstack_api', 'username')
stack_api = settings_parser.get('browserstack_api', 'key')


class TestBase(unittest.TestCase):

    def setUp(self):
        self.base_url = settings_parser.get('url', 'base_url')
        if settings_parser.get('location', 'location') == 'local_ios':
            self.driver = webdriver.Remote(
            command_executor='http://127.0.0.1:4723/wd/hub',
            desired_capabilities={
                'platformName': 'iOS',
                'platformVersion': '8.3',
                'deviceName': 'iPhone 6'
                })
            self.driver.implicitly_wait(10)
        elif settings_parser.get('location', 'location') == 'local_droid':
            self.driver = webdriver.Remote(
            command_executor='http://127.0.0.1:4723/wd/hub',
            desired_capabilities={
                        'platformName': 'Android',
                        'platformVersion': '4.4',
                        'deviceName': 'Android Emulator'
                    })
        elif settings_parser.get('location', 'location') == 'local':
            if settings_parser.get('local_settings', 'browser') == 'firefox':
                self.driver = webdriver.Firefox()
                self.driver.set_window_size(2000, 2000)
            elif settings_parser.get('local_settings', 'browser') == 'chrome':
                self.driver = webdriver.Chrome()
                self.driver.set_window_size(2000, 2000)
        elif settings_parser.get('location', 'location') == 'local_X':
            if settings_parser.get('local_settings', 'browser') == 'firefox':
                self.driver = webdriver.Firefox()
                self.driver.set_window_size(2000, 2000)

                self.driver2 = webdriver.Firefox()
            elif settings_parser.get('local_settings', 'browser') == 'chrome':
                chrome_options = Options()
                chrome_options.add_argument("--disable-component-update")
                chrome_options.add_argument("--always-authorize-plugins")
                chrome_options.add_argument("--allow-outdated-plugins")
                chrome_options.add_argument("--ppapi-flash-path=/usr/lib/adobe-flashplugin/libpepflashplayer.so")
                self.driver = webdriver.Chrome(chrome_options=chrome_options)
                # self.driver = webdriver.Chrome()
                self.driver.set_window_size(2000, 2000)

                # self.driver2 = webdriver.Chrome()
                self.driver2 = webdriver.Chrome(chrome_options=chrome_options)
        elif settings_parser.get('location', 'location') == 'grid':
            if settings_parser.get('grid', 'browser') == 'firefox':
                self.driver = webdriver.Remote(
                    desired_capabilities=DesiredCapabilities.FIREFOX,
                    command_executor='http://' + settings_parser.get('grid', 'grid_ip') + ':4444/wd/hub',
                    browser_profile=None, proxy=None,
                    keep_alive=True
                )
            elif settings_parser.get('grid', 'browser') == 'chrome':
                self.driver = webdriver.Remote(
                   desired_capabilities=DesiredCapabilities.CHROME,
                   command_executor='http://' + settings_parser.get('grid', 'grid_ip') + ':4444/wd/hub',
                   browser_profile=None, proxy=None,
                   keep_alive=True
                )
        elif settings_parser.get('location', 'location') == 'grid_X':
            if settings_parser.get('grid', 'browser') == 'firefox':
                self.driver = webdriver.Remote(
                    desired_capabilities=DesiredCapabilities.FIREFOX,
                    command_executor='http://' + settings_parser.get('grid', 'grid_ip') + ':4444/wd/hub',
                    browser_profile=None, proxy=None,
                    keep_alive=True
                )
                self.driver2 = webdriver.Remote(
                    desired_capabilities=DesiredCapabilities.FIREFOX,
                    command_executor='http://' + settings_parser.get('grid', 'grid_ip') + ':4444/wd/hub',
                    browser_profile=None, proxy=None,
                    keep_alive=True
                )
            elif settings_parser.get('grid', 'browser') == 'chrome':
                self.driver = webdriver.Remote(
                   desired_capabilities=DesiredCapabilities.CHROME,
                   command_executor='http://' + settings_parser.get('grid', 'grid_ip') + ':4444/wd/hub',
                   browser_profile=None, proxy=None,
                   keep_alive=True
                )
                self.driver2 = webdriver.Remote(
                    desired_capabilities=DesiredCapabilities.CHROME,
                    command_executor='http://' + settings_parser.get('grid', 'grid_ip') + ':4444/wd/hub',
                    browser_profile=None, proxy=None,
                    keep_alive=True
                )
        elif settings_parser.get('location', 'location') == 'grid_ios':
                self.driver = webdriver.Remote(
                    command_executor='http://' + settings_parser.get('grid', 'grid_ip') + ':4444/wd/hub',
                    desired_capabilities={
                        'browserName': 'Safari',
                        'platformName': 'iOS',
                        'deviceName': 'iPhone 6'
                    })
        elif settings_parser.get('location', 'location') == 'grid_droid':
                self.driver = webdriver.Remote(
                    command_executor='http://' + settings_parser.get('grid', 'grid_ip') + ':4444/wd/hub',
                    desired_capabilities={
                        'browserName': 'Browser',
                        'platformName': 'Android',
                        'platformVersion': '4.4',
                        'deviceName': 'emulator-5554'
                    })
        elif settings_parser.get('location', 'location') == 'browserstack':
            bs_os = settings_parser.get('browserstack_caps', 'os')
            bs_platform = settings_parser.get('browserstack_caps', 'platform')
            bs_browser = settings_parser.get('browserstack_caps', 'browser')
            bs_browser_v = settings_parser.get('browserstack_caps', 'version')
            bs_resolution = settings_parser.get('browserstack_caps', 'resolution')
            bs_video = settings_parser.get('browserstack_caps', 'video')
            self.driver = webdriver.Remote(
                command_executor='http://' + stack_username + ':' + stack_api + '@hub.browserstack.com:80/wd/hub',
                desired_capabilities={
                    'os': bs_os,
                    'os_version': bs_platform,
                    'browser': bs_browser,
                    'browser_version': bs_browser_v,
                    'resolution': bs_resolution,
                    'browserstack.debug': True,
                    'browserstack.video': bs_video,
                    'browserstack.local': True,
                    'acceptSslCerts': True,
                    'name': "\n%s %s %s %s %s" % (type(self).__name__, bs_browser, bs_browser_v, bs_os, bs_platform)
                })
            self.driver.implicitly_wait(20)
        elif settings_parser.get('location', 'location') == 'browserstack_X':

            r = requests.get('https://www.browserstack.com/automate/plan.json',
                             auth=(stack_username, stack_api))
            sessions_running = r.json()['parallel_sessions_running']
            sessions_queued = r.json()['queued_sessions']

            while int(sessions_queued) or int(sessions_running) > 0:
                r = requests.get('https://www.browserstack.com/automate/plan.json',
                                 auth=(stack_username, stack_api))
                sessions_running = r.json()['parallel_sessions_running']
                sessions_queued = r.json()['queued_sessions']
                time.sleep(5)
                if int(sessions_queued) or int(sessions_running) is 0:
                    break

            bs_os = settings_parser.get('browserstack_caps', 'os')
            bs_platform = settings_parser.get('browserstack_caps', 'platform')
            bs_browser = settings_parser.get('browserstack_caps', 'browser')
            bs_browser_v = settings_parser.get('browserstack_caps', 'version')
            bs_resolution = settings_parser.get('browserstack_caps', 'resolution')
            bs_video = settings_parser.get('browserstack_caps', 'video')
            test_name = "\n%s" % type(self).__name__
            self.driver = webdriver.Remote(
                command_executor='http://' + stack_username + ':' + stack_api + '@hub.browserstack.com:80/wd/hub',
                desired_capabilities={
                    'os': bs_os,
                    'os_version': bs_platform,
                    'browser': bs_browser,
                    'browser_version': bs_browser_v,
                    'resolution': bs_resolution,
                    'browserstack.debug': True,
                    'browserstack.video': bs_video,
                    'browserstack.local': True,
                    'acceptSslCerts': True,
                    'name': test_name
                })
            self.driver.implicitly_wait(20)
            self.driver2 = webdriver.Remote(
                command_executor='http://' + stack_username + ':' + stack_api + '@hub.browserstack.com:80/wd/hub',
                desired_capabilities={
                    'os': bs_os,
                    'os_version': bs_platform,
                    'browser': bs_browser,
                    'browser_version': bs_browser_v,
                    'resolution': bs_resolution,
                    'browserstack.debug': True,
                    'browserstack.video': bs_video,
                    'browserstack.local': True,
                    'acceptSslCerts': True,
                    'name': test_name + ' ' + str(2)
                })
            self.driver2.implicitly_wait(20)
        elif settings_parser.get('location', 'location') == 'browserstack_mobile_ios':
            bs_ios_browser = settings_parser.get('browserstack_ios_caps', 'browser')
            bs_ios_platform = settings_parser.get('browserstack_ios_caps', 'platform')
            bs_ios_device = settings_parser.get('browserstack_ios_caps', 'device')
            self.driver = webdriver.Remote(
                command_executor='http://' + stack_username + ':' + stack_api + '@hub.browserstack.com:80/wd/hub',
                desired_capabilities={
                    'browserName': bs_ios_browser,
                    'platform': bs_ios_platform,
                    'device': bs_ios_device,
                    'browserstack.debug': True,
                    'browserstack.video': True,
                    'name': "\n%s" % type(self).__name__
                })
            self.driver.implicitly_wait(10)
        elif settings_parser.get('location', 'location') == 'browserstack_mobile_droid':
            bs_droid_browser = settings_parser.get('browserstack_droid_caps', 'browser')
            bs_droid_platform = settings_parser.get('browserstack_droid_caps', 'platform')
            bs_droid_device = settings_parser.get('browserstack_droid_caps', 'device')
            self.driver = webdriver.Remote(
                command_executor='http://' + stack_username + ':' + stack_api + '@hub.browserstack.com:80/wd/hub',
                desired_capabilities={
                    'browserName': bs_droid_browser,
                    'platform': bs_droid_platform,
                    'device': bs_droid_device,
                    'browserstack.debug': True,
                    'browserstack.video': True,
                    'name': "\n%s" % type(self).__name__
                })
            self.driver.implicitly_wait(10)

    def tearDown(self):
        if settings_parser.get('location', 'location') == 'browserstack':
            r = requests.get('https://www.browserstack.com/automate/sessions/' + self.driver.session_id + '.json',
                              auth=(stack_username, stack_api))
            print "Link to your job: " + r.json()['automation_session']['browser_url']
            self.driver.quit()
        elif settings_parser.get('location', 'location') == 'browserstack_X' or \
                settings_parser.get('location', 'location') == 'local_X' or \
                settings_parser.get('location', 'location') == 'grid_X':
            self.driver.quit()
            self.driver2.quit()
        else:
            self.driver.quit()
