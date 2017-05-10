import os
import json
from filepath import FilePath
import re
from runner_aggregator import suite_runner_lib_repo

THIS_DIR = os.path.join(__file__, os.pardir)
LIB_PATH = os.path.abspath(os.path.join(THIS_DIR, os.pardir))


class GatherElements(object):

    def gather_elements(self, loc, test_type, template_name):
        locator = {}
        fp = FilePath()
        structure = fp.get_filepaths('{lib_path}/{lib_repo}/elements/{test_type}/{template}'.format(lib_path=LIB_PATH,
                                                                                         test_type=test_type,
                                                                                         template=template_name,
                                                                                         lib_repo=suite_runner_lib_repo()))
        for element_file in structure:
            with open(element_file) as elements_map:
                if bool(re.search(loc, element_file)) is True:
                    elements = json.load(elements_map)
                    for element_tag, element_value in elements.iteritems():
                        locator[element_tag] = element_value

        return locator
