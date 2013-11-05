import json
from datetime import datetime,timedelta
import pprint
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt

class Answers:

    def __init__(self, json = None, csv = None, dataframe = None):
        if json:
            self.data = self._init_data_from_json(json)
        elif csv:
            self.data = pd.DataFrame.from_csv(csv)
        else:
            self.data = dataframe

    @classmethod
    def from_json(cls, filename):
        return Answers(json = filename)

    @classmethod
    def from_csv(cls, filename):
        return Answers(csv = filename)

    @classmethod
    def from_dataframe(cls, dataframe):
        return Answers(dataframe = dataframe)

    def __getitem__(self, key):
        if np.isscalar(key):
            return self.data[key]
        else:
            return Answers(dataframe = self.data[key])

    def __setitem__(self, key, value):
        self.data[key] = value

    def __len__(self):
        return len(self.data)

    def sort(self, columns = None, column = None, axis = 0, ascending = True,
             inplace = False):
        if inplace:
            self.data.sort(
                columns = columns,
                column = column,
                axis = axis,
                ascending = ascending,
                inplace = True)
            return self
        else:
            sorted_data = self.data.sort(
                columns = columns,
                column = column,
                axis = axis,
                ascending = ascending)
            return Answers.from_dataframe(sorted_data)

    def to_csv(self, filename):
        self.data.to_csv(filename, index = False)

    def normalize_response_time(self, column, inplace = False):
        result = pd.DataFrame()
        for key in self.data[column].unique():
            key_data = self.data[self.data[column] == key]
            mean = key_data['response.time'].mean()
            key_data['response.time'] = key_data['response.time'] - mean
            result = result.append(key_data)
        if inplace:
            self.data = result
            return self
        else:
            return Answers.from_dataframe(result)

    def correct_answers(self):
        return Answers.from_dataframe(
            self.data[self.data["place.asked"] == self.data["place.answered"]])

    def wrong_answers(self):
        return Answers.from_dataframe(
            self.data[self.data["place.asked"] != self.data["place.answered"]])

    def _init_data_from_json(self, filename):
        try:
            file = open(filename)
            raw_data = json.load(file)
        finally:
            file.close()
        data = self._reorganize_raw(raw_data)
        data = self._recognize_sessions(data)
        data = self._compute_question_types(data)
        return data

    def _reorganize_raw(self, raw_data):
        data = pd.DataFrame()
        for item in raw_data:
            if item["model"] != "questions.answer":
                continue
            fields = item["fields"]
            answer = fields["answer"]
            inserted = datetime.strptime(fields["askedDate"], "%Y-%m-%dT%H:%M:%S")
            new_row = pd.DataFrame({
                "response.time"  : [math.log(fields["msResposeTime"])],
                "place.asked"    : [fields["place"]],
                "place.answered" : [answer],
                "user"           : [fields["user"]],
                "options.number" : [len(fields["options"])],
                "inserted"       : [inserted],
                "type"           : [fields["type"]]})
            data = data.append(new_row)
        return data

    def _recognize_sessions(self, data):
        data = data.sort(["user", "inserted"])
        previous_time = None
        previous_user = None
        session_id = 0
        result = pd.DataFrame()
        for i, row in data.iterrows():
            if (previous_time == None or
                previous_user != row["user"] or
                row["inserted"] - previous_time > timedelta(minutes = 30)):
                session_id = session_id + 1
            previous_time = row["inserted"]
            previous_user = row["user"]
            to_append = row.to_dict()
            to_append["session"] = [session_id]
            result = result.append(pd.DataFrame(to_append))
        return result

    def _compute_question_types(self, data):
        data = data.sort(["user", "place.asked", "inserted"])
        previous_place = None
        previous_user = None
        question_count_all = None
        question_count_wrong = None
        question_count_correct = None
        result = pd.DataFrame()
        for i, row in data.iterrows():
            if (previous_user == None or
                previous_user != row["user"] or
                previous_place != row["place.asked"]):
                question_count_all = 0
                question_count_wrong = 0
                question_count_correct = 0
            to_append = row.to_dict()
            to_append["question.number.all"] = [question_count_all]
            to_append["question.number.correct"] = [question_count_correct]
            to_append["question.number.wrong"] = [question_count_wrong]
            result = result.append(pd.DataFrame(to_append))
            question_count_all = question_count_all + 1
            if (row["place.answered"] and row["place.answered"] == row["place.asked"]):
                question_count_correct = question_count_correct + 1
            else:
                question_count_wrong = question_count_wrong + 1
            previous_place = row["place.asked"]
            previous_user = row["user"]
        return result
