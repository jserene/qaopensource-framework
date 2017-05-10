import os
import re
import json

# print test
THIS_DIR = os.path.join(__file__, os.pardir)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.abspath(os.path.join(ROOT_DIR, '../../'))

def suite_runner_test_repo():
    with open('{root_path}/runner_opts.json'.format(root_path=ROOT_PATH)) as data_file:
        runner_data = json.load(data_file)
        return runner_data['test_repo']

TEST_PATH = os.path.abspath(os.path.join(THIS_DIR, '../../tests'))
TEST_PATH = os.path.abspath(os.path.join(THIS_DIR, '../../tests/{test_repo}/'.format(test_repo=suite_runner_test_repo())))


# print test
# print TEST_PATH
# print TEST_PATH2


class FilePath(object):

    # Walk through directory structure
    def get_filepaths(self, directory):
        file_paths = []
        for root, directories, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)

        return file_paths

    # Generate dictionary of all available projects, templates, test suites
    # and tests
    def get_project_options(self):
        proj_names = []
        test_types = []
        template_names = []
        test_suites = []
        single_test_names = []
        for all_files in self.get_filepaths(TEST_PATH):
            try:
                test_types.append(str(all_files.split('/')[7]))
            except IndexError:
                pass

        test_types = list(set(test_types))
        cleaned_test_types = []

        project_options = {}
        for iter_test_types in xrange(len(test_types)):
            if bool(re.search(r'.py', test_types[iter_test_types])) is False:
                cleaned_test_types.append(test_types[iter_test_types])

        for i in xrange(len(cleaned_test_types)):
            project_options['Test_Type_{0}'.format(i + 1)] = cleaned_test_types[i]

        for list_projects in self.get_filepaths(TEST_PATH):
            proj_names.append(str(list_projects.split('/')[5]))
        proj_names = list(set(proj_names))

        cleaned_proj_names = []

        for iter_projects in xrange(len(proj_names)):
            if bool(re.search(r'.py', proj_names[iter_projects])) is False:
                cleaned_proj_names.append(proj_names[iter_projects])

        for i in xrange(len(cleaned_proj_names)):
            project_options['Project_{0}'.format(i + 1)] = cleaned_proj_names[i]

        for list_templates in self.get_filepaths(TEST_PATH):
            try:
                if bool(re.search(r'template', list_templates)) is True:
                    template_names.append(str(list_templates.split('/')[7]))
            except IndexError:
                pass

        template_names = list(set(template_names))

        for iter_templates in xrange(len(template_names)):
            project_options['Template_{0}'.format(iter_templates + 1)] = template_names[iter_templates]

        for list_test_suites in self.get_filepaths(TEST_PATH):
            try:
                test_suites.append(str(list_test_suites.split('/')[8]))
            except IndexError:
                pass

        test_suites = list(set(test_suites))

        for iter_test_suites in xrange(len(test_suites)):
            try:
                if bool(re.search(r'.py', test_suites[iter_test_suites])) is True:
                    pass
                else:
                    project_options['Test_Suite_{0}'.format(iter_test_suites + 1)] = test_suites[iter_test_suites]
            except IndexError:
                pass

        for list_single_tests in self.get_filepaths(TEST_PATH):
            try:
                single_test_names.append(str(list_single_tests.split('/')[9]))
            except IndexError:
                pass

        single_test_names = list(set(single_test_names))

        for iter_single_test in xrange(len(single_test_names)):
            try:
                if bool(re.search(r'.pyc', single_test_names[iter_single_test])) is True:
                    pass
                else:
                    project_options['Indy_Test_{0}'.format(iter_single_test + 1)] = single_test_names[iter_single_test]
            except IndexError:
                pass

        return project_options

    # The following functions are passed into the suite runner
    # and the under construction interface
    def prj_names(self):
        all_project_options = self.get_project_options()
        prj_names = []
        for project_key, project_value in all_project_options.iteritems():
            if bool(re.search(r'Project', str(project_key))) is True:
                prj_names.append(project_value)
        return prj_names

    def test_types(self):
        all_project_options = self.get_project_options()
        test_types = []
        for test_type_key, test_type_value in all_project_options.iteritems():
            if bool(re.search(r'Test_Type', str(test_type_key))) is True:
                if bool(re.search(r'init', str(test_type_value))) is False:
                    test_types.append(test_type_value)

        return test_types

    def template_names(self):
        all_project_options = self.get_project_options()
        template_names = []
        for template_key, template_value in all_project_options.iteritems():
            if bool(re.search(r'Template', str(template_key))) is True:
                if bool(re.search(r'init', str(template_value))) is False:
                    template_names.append(template_value)

        return template_names

    def test_suites(self):
        all_project_options = self.get_project_options()
        test_suites = []
        for project_key, project_value in all_project_options.iteritems():
            if bool(re.search(r'Test_Suite', str(project_key))) is True:
                if bool(re.search(r'init', str(project_value))) is False:
                    test_suites.append(project_value)

        return test_suites

    def single_test_names(self):
        all_project_options = self.get_project_options()
        sgl_test = []
        for single_test_key, single_test_value in all_project_options.iteritems():
            if bool(re.search(r'Indy_Test', str(single_test_key))) is True:
                if bool(re.search(r'init', str(single_test_value))) is False:
                    sgl_test.append(single_test_value)

        return sgl_test


# fp = FilePath()
# print fp.get_filepaths(TEST_PATH)[2].split('/')[5]
# tt = []
# for directories in fp.get_filepaths(TEST_PATH):
#     # tt.append(directories.split('/'))
#     print directories
#
# print tt
