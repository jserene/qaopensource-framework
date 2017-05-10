import pymysql.cursors
import pymysql
import os
import json
from test_suite_aggregator import TestSuiteAggregator
from pymongo import MongoClient
from bson import ObjectId
from runner_aggregator import suite_runner_lib_repo


THIS_DIR = os.path.join(__file__, os.pardir)
LIB_PATH = os.path.abspath(os.path.join(THIS_DIR, os.pardir))
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.abspath(os.path.join(ROOT_DIR, '../../'))

tsa = TestSuiteAggregator()


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class DBEnv(object):

    def collect_from_config(self, template):
        tmp_cln = []
        collect_env = tsa.collect_environments().split(',')
        for environment in collect_env:
            tmp_cln.append(environment.replace(' ', ''))

        env_list = []
        for env_filter in tmp_cln:
            env_split = env_filter.split('_')[-1]
            env_list.append(env_split)
        # Generates a list of available environments
        env_list = list(set(env_list))

        # Generates a list associating available environments
        # with their template names
        template_list = []
        template_to_query = []
        for template_env in tmp_cln:
            env_rep = template_env.split('_')[-1]
            rebuild_template_name = template_env.replace(env_rep, 'template')
            template_list.append(rebuild_template_name)

        # Finds the template associated with environment config.
        # This generates a list of valid templates.
        for template_name in template_list:
            if len(template) == len(template_name) and template == template_name:
                template_to_query.append(template_name)

        # When the suite_runner is executed it creates a json file
        # in the project root with user input options we can use
        with open('{project_root}/runner_opts.json'.format(project_root=ROOT_PATH)) as data_file:
            runner_data = json.load(data_file)

        config_file = '{lib_path}/{lib_repo}/config/environments/{test_env}/{config}.json'\
            .format(lib_path=LIB_PATH,
                    test_env=runner_data['test_env'],
                    config=template_to_query[0],
                    lib_repo=suite_runner_lib_repo())

        return config_file


class MysqlConnect(object):

    def db_connect(self, template, query):
        dbenv = DBEnv()
        with open(dbenv.collect_from_config(template)) as data_file:
            data = json.load(data_file)
            for config_key, config_value in data.iteritems():
                print config_key, config_value
                print config_value['db_test_settings']['db_name']

                conn = pymysql.connect(host=config_value['db_test_settings']['db_hostname'],
                                       user=config_value['db_test_settings']['db_user'],
                                       password=config_value['db_test_settings']['db_password'],
                                       db=config_value['db_test_settings']['db_name'],
                                       charset='utf8mb4',
                                       cursorclass=pymysql.cursors.DictCursor)
                conn.autocommit(True)

                try:
                    with conn.cursor() as cursor:
                        sql = query
                        cursor.execute(sql)

                    conn.commit()
                    result = cursor.fetchone()
                    print (result)
                finally:
                    conn.close()

                return result


class MongoDBConnection(object):

    def mongo_connection(self, template):
        dbenv = DBEnv()
        with open(dbenv.collect_from_config(template)) as data_file:
            data = json.load(data_file)
            for config_key, config_value in data.iteritems():
                print config_key
                print config_value
                mongo_client = MongoClient('mongodb://{mongo_host}:{mongo_port}/'
                                           .format(mongo_host=config_value['db_test_settings']['db_hostname'],
                                                   mongo_port=config_value['db_test_settings']['db_port']))
                return mongo_client

    def mongo_find_one_collection(self, template, db_name, collection_name, collection_key, collection_value):
        mongo_conn = self.mongo_connection(template)
        db = mongo_conn[db_name]
        collection = db[collection_name]
        query = collection.find_one({"{coll_key}"
                                    .format(coll_key=collection_key): "{coll_value}"
                                    .format(coll_value=collection_value)})
        return query

    def mongo_delete_one_collection(self, template, db_name, collection_name, collection_key, collection_value):
        mongo_conn = self.mongo_connection(template)
        db = mongo_conn[db_name]
        collection = db[collection_name]
        delete_this = collection.find_one_and_delete({"{coll_key}"
                                                      .format(coll_key=collection_key): "{coll_value}"
                                                      .format(coll_value=collection_value)})
