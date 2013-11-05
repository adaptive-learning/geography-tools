import json
import pandas as pd


class Places:

    def __init__(self, json = None, csv = None, dataframe = None):
        if json != None:
            self.data = self._init_data_from_json(json)
        elif csv != None:
            self.data = pd.DataFrame.from_csv(csv)
        elif dataframe != None:
            self.data = dataframe
        else:
            raise Exception("There is no way how to build a new instance.")

    @classmethod
    def from_json(cls, filename):
        return Places(json = filename)

    @classmethod
    def from_csv(cls, filename):
        return Places(csv = filename)

    @classmethod
    def from_dataframe(cls, dataframe):
        return Places(dataframe = dataframe)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def to_csv(self, filename):
        self.data.to_csv(filename, index = False)

    def _init_data_from_json(self, filename):
        try:
            file = open(filename)
            raw_data = json.load(file)
        finally:
            file.close()
        data = self._reorganize_raw(raw_data)
        return data

    def _reorganize_raw(self, raw_data):
        data = []
        for item in raw_data:
            if item['model'] != 'core.place':
                continue
            fields = item['fields']
            data.append({
                'id'   : item['pk'],
                'name' : fields['name'].encode('utf8'),
                'type' : fields['type'],
                'code' : fields['code']})
        return pd.DataFrame(data)
