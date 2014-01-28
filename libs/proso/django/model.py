# -*- coding: utf-8 -*-
import json
import pandas as pd
import re
from datetime import datetime


def json2csv(model_name, json_file, csv_file):
    try:
        f = open(json_file)
        json_data = json.load(f)
        dataframe = json2dataframe(model_name, json_data)
        dataframe.to_csv(csv_file, index=False, encoding='utf-8')
    finally:
        f.close()


def json2dataframe(model_name, json_data):
    data = []
    for item in json_data:
        if item['model'] != model_name:
            continue
        fields = item['fields']
        row = {'id': item['pk']}
        for key, value in fields.iteritems():
            row[key] = value
        data.append(row)
    return pd.DataFrame(data)
