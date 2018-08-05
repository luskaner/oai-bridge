import traceback

from flask_testing import LiveServerTestCase
from sickle import Sickle
from sickle.oaiexceptions import NoRecordsMatch

import OAIBridge


class TestListRecords(LiveServerTestCase):
    sickles = {}

    def create_app(self):
        self.set_config()
        app = OAIBridge.app
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 0
        return app

    def set_config(self):
        pass

    def _test(self, context, params):
        num_bridge_records, bridge_records = self.get_bridge_records(context, params)
        num_direct_records, direct_records = TestListRecords.get_direct_records(context, params)
        self.assertEqual(num_direct_records, num_bridge_records)
        self.assertCountEqual(direct_records, bridge_records)

    def get_bridge_records(self, context, params):
        records = []
        i = 0
        from sickle.oaiexceptions import NoRecordsMatch
        try:
            for record in self.sickles[context].ListRecords(**params):
                i += 1
                if not record.deleted:
                    records.append(record.metadata)
        except NoRecordsMatch:
            pass
        except:
            print(traceback.format_exc())
            pass
        return i, records

    @staticmethod
    def get_direct_records(context, params):
        records = []
        i = 0
        root = OAIBridge.data["contexts"][context]
        for name in root:
            sickle = Sickle(root[name]['url'])
            sets = root[name]['sets'] if 'sets' in root[name] else None
            if not sets:
                try:
                    for record in sickle.ListRecords(**params):
                        i += 1
                        if not record.deleted:
                            records.append(record.metadata)
                except NoRecordsMatch:
                    pass
                except:
                    print(traceback.format_exc())
                    break
            else:
                unknown_error = False
                for set_name in sets:
                    new_params = dict(params)
                    new_params['set'] = set_name
                    try:
                        for record in sickle.ListRecords(**new_params):
                            i += 1
                            if not record.deleted:
                                records.append(record.metadata)
                    except NoRecordsMatch:
                        pass
                    except:
                        print(traceback.format_exc())
                        unknown_error = True
                        break
                if unknown_error:
                    break
        return i, records
