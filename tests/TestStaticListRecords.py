import os

from sickle import Sickle

import OAIBridge
import timeout_decorator

from tests.TestListRecords import TestListRecords


class TestStaticListRecords(TestListRecords):

    def set_config(self):
        with open(os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__))) + '/configuration.yaml', 'r') as configuration:
            OAIBridge.data = OAIBridge.set_config(OAIBridge.load(configuration))

    def setUp(self):
        self.sickles = {
            'TEST_NO_SET_START': Sickle(self.get_server_url() + "/TEST_NO_SET_START"),
            'TEST_NO_SET_END': Sickle(self.get_server_url() + "/TEST_NO_SET_END"),
            'TEST_FAIL_STARt': Sickle(self.get_server_url() + "/TEST_FAIL_START"),
            'TEST_FAIL_END': Sickle(self.get_server_url() + "/TEST_FAIL_END")
        }

    @timeout_decorator.timeout(180)
    def test_from_until_no_set_start(self):
        self._test(
            "TEST_NO_SET_START",
            {'metadataPrefix': 'oai_dc', 'from': '2016-01-01', 'until': '2016-02-01'}
        )

    @timeout_decorator.timeout(180)
    def test_until_no_set_start(self):
        self._test(
            "TEST_NO_SET_START",
            {'metadataPrefix': 'oai_dc', 'until': '2009-10-01'}
        )

    @timeout_decorator.timeout(180)
    def test_from_no_set_start(self):
        self._test(
            "TEST_NO_SET_START",
            {'metadataPrefix': 'oai_dc', 'from': '2018-07-02'}
        )

    @timeout_decorator.timeout(180)
    def test_from_until_no_set_end(self):
        self._test(
            "TEST_NO_SET_END",
            {'metadataPrefix': 'oai_dc', 'from': '2016-01-01', 'until': '2016-02-01'}
        )

    @timeout_decorator.timeout(180)
    def test_until_no_set_end(self):
        self._test(
            "TEST_NO_SET_END",
            {'metadataPrefix': 'oai_dc', 'until': '2009-10-01'}
        )

    @timeout_decorator.timeout(180)
    def test_from_no_set_end(self):
        self._test(
            "TEST_NO_SET_END",
            {'metadataPrefix': 'oai_dc', 'from': '2018-07-02'}
        )

    @timeout_decorator.timeout(180)
    def test_fail_start(self):
        self._test(
            "TEST_FAIL_START",
            {'metadataPrefix': 'oai_dc', 'from': '2018-07-02'}
        )

    @timeout_decorator.timeout(180)
    def test_fail_end(self):
        self._test(
            "TEST_FAIL_END",
            {'metadataPrefix': 'oai_dc', 'from': '2018-07-02'}
        )