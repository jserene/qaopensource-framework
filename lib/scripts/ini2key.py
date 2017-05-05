#!/usr/bin/env python

from lib.src import configure

if __name__ == '__main__':
    config = configure.read_config()
    browserstack_key = config.get('browserstack_api', 'key')
    print(browserstack_key)
