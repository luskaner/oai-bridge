import datetime
import traceback

from sickle import Sickle

import OAIBridge
import timeout_decorator
from lxml import etree
import requests
import random

from tests.TestListRecords import TestListRecords


class TestDynamicListRecords(TestListRecords):

    def set_config(self):
        OAIBridge.data = self._get_random_configuration()

    def setUp(self):
        self.sickles = {'TEST': Sickle(self.get_server_url() + "/TEST")}

    @timeout_decorator.timeout(600)
    def _test_random(self):
        params = {'metadataPrefix': 'oai_dc'}
        date_format = '%Y-%m-%d'
        min_date = datetime.datetime(2010, 1, 1)
        max_date = datetime.datetime.now()
        pass_from_date = bool(random.getrandbits(1))
        if pass_from_date:
            from_date = TestDynamicListRecords._random_date(min_date, max_date)
            params['from'] = from_date.strftime(date_format)
        pass_until_date = bool(random.getrandbits(1))
        if pass_until_date:
            if pass_from_date:
                until_date = TestDynamicListRecords._random_date(from_date, max_date)
            else:
                until_date = TestDynamicListRecords._random_date(min_date, max_date)
            params['until'] = until_date.strftime(date_format)
        print("Using Configuration:")
        print(OAIBridge.data)
        self._test('TEST', params)

    def test_random_multiple(self):
        for _ in range(10):
            try:
                self.set_config()
                self.setUp()
                self._test_random()
            except:
                print(traceback.format_exc())
                pass

    @staticmethod
    def _get_servers():
        servers = []
        xml = etree.fromstring(requests.get('http://www.openarchives.org/pmh/registry/ListFriends').content)
        for url in xml.findall('.//baseURL'):
            servers.append(url.text)
        return servers

    @staticmethod
    def _random_date(start, end):
        return start + datetime.timedelta(
            seconds=random.randint(0, int((end - start).total_seconds())),
        )

    @timeout_decorator.timeout(60)
    def _get_random_configuration(self):
        self.servers = TestDynamicListRecords._get_servers()
        test_key = 'TEST'
        configuration = {'contexts': {test_key: {}}}
        servers = random.choices(self.servers, k=random.randint(1, min(3, len(self.servers))))
        i = 0
        for server in servers:
            server_key = 'SERVER' + str(i)
            configuration['contexts'][test_key][server_key] = {'url': server}
            set_names = []
            server_sickle = Sickle(server)
            try:
                for set_name in server_sickle.ListSets():
                    if len(set_names) == 20:
                        break
                    set_names.append(set_name.setSpec)
            except:
                continue
            sets = set(random.choices(set_names, k=random.randint(0, min(20, len(set_names)))))
            if len(sets) > 0:
                configuration['contexts'][test_key][server_key]['sets'] = []
            for set_name in sets:
                configuration['contexts'][test_key][server_key]['sets'].append(set_name)
            i += 1
        return configuration
