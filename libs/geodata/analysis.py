import sys
from geodata import Answers, Places
import geodata
import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np
import pandas as pd
import math
from pprint import pprint
import os
import os.path
from colorsys import hsv_to_rgb


class GeneralAnalysis:

    def __init__(self, filename_csv = None, answers = None):
        if filename_csv:
            self.answers = Answers.from_csv(filename_csv)
        elif answers:
            self.answers = answers
        else:
            raise Exception("Can't create a new analysis object.")

    def __getitem__(self, key):
        if np.isscalar(key):
            return self.answers[key]
        else:
            return self.new_from_answers(self.answers[key])

    def __setitem__(self, key, value):
        self.answers[key] = value

    def new_from_answers(self, answers):
        raise Exception("Method 'new_from_answers should be overriden.")

class PlotAnalysis(GeneralAnalysis):

    def __init__(self, filename_csv = None, answers = None):
        GeneralAnalysis.__init__(self, filename_csv, answers)

    def plot_time_hist(self, correct = True):
        xmax = max(
            self.answers.wrong_answers()["response.time"].max(),
            self.answers.correct_answers()["response.time"].max())
        data = None
        color = None
        label = None
        if correct:
            data = self.answers.correct_answers()
            color = "green"
            label = "Correct Answers"
        else:
            data = self.answers.wrong_answers()
            color = "red"
            label = "Wrong Answers"
        plt.hist(
            data['response.time'],
            bins = 20,
            color = color,
            label = label)
        plt.xlabel("Response Time (log)")
        plt.xlim(0, xmax)

    def plot_time_density(self, correct = True):
        xmax = max(
            self.answers.wrong_answers()["response.time"].max(),
            self.answers.correct_answers()["response.time"].max())
        data = None
        color = None
        label = None
        if correct:
            data = self.answers.correct_answers()
            color = "green"
            label = "Correct Answers"
        else:
            data = self.answers.wrong_answers()
            color = "red"
            label = "Wrong Answers"
        xs = np.linspace(0,xmax,1000)
        density = stats.gaussian_kde(data['response.time'])
        plt.plot(xs, density(xs), color = color, label = label)
        plt.xlabel("Response Time (log)")
        plt.ylabel("Probability")

    def plot_pattern_times_density(self, pattern, plot, labels, normalize = None):
        if len(pattern) != len(plot):
            raise Exception("The length of pattern and plot lists doesn't match")
        data = self._get_pattern_times(pattern, normalize = normalize)
        xmin = min(map(lambda df: df['response.time'].min(), data))
        xmax = max(map(lambda df: df['response.time'].max(), data))
        xs = np.linspace(xmin, xmax, 1000)
        for i in range(len(pattern)):
            if plot[i]:
                plt.plot(
                    xs,
                    stats.gaussian_kde(data[i]['response.time'])(xs),
                    label = labels[i])

    def _get_pattern_times(self, pattern, normalize = None):
        data = self.answers
        data = data.sort(['place.asked', 'inserted'])
        data['response.time'] = np.log(data['response.time'])
        if normalize != None:
            data.normalize_response_time(normalize, inplace = True)
        data = data.data
        result = []
        for i in pattern:
            result.append(pd.DataFrame())
        search = []
        for user in data['user'].unique():
            user_data = data[data['user'] == user]
            for i, row in user_data.iterrows():
                search.append(row)
                if len(search) < len(pattern):
                    continue
                elif len(search) > len(pattern):
                    search = search[1:]
                pattern_match = True
                for i in range(len(pattern)):
                    if pattern[i] != (
                        search[i]['place.asked'] == search[i]['place.answered']):
                        pattern_match = False
                        break
                if not pattern_match:
                    continue
                for i in range(len(pattern)):
                    result[i] = result[i].append(pd.DataFrame([search[i].to_dict()]))
        return result

    def new_from_answers(self, answers):
        return PlotAnalysis(answers = answers)


class MapAnalysis(GeneralAnalysis):

    def __init__(self, kartograph, shapefile, places_csv = None, places = None, answers_csv = None, answers = None):
        GeneralAnalysis.__init__(self, answers_csv, answers)
        if places_csv:
            self.places = Places.from_csv(places_csv)
        else:
            self.places = places
        self.shapefile = shapefile
        self.kartograph = kartograph

    def new_from_answers(self, answers):
        return MapAnalysis(
            kartograph = self.kartograph,
            shapefile = self.shapefile,
            places = self.places,
            answers = answers)

    def difficulties_from_model(self, model, out_svg):
        difficulties = model.difficulties(self.places)
        self._save(
            difficulties,
            self._config_world(),
            out_svg,
            out_svg + ".css")

    def model_seq_for_user(self, model, user, dest_dir, ratio = 'probability'):
        simulator = geodata.Simulator(self.answers)
        simulator_user = simulator[simulator['user'] == user]
        simulator = simulator[simulator['user'] != user]
        simulator.simulate(model)
        simulation = simulator_user.step_by_step(model)
        dest_dir_path = os.path.join(os.path.abspath(dest_dir), "user_seq_" + str(user))
        if not os.path.exists(dest_dir_path):
            os.makedirs(dest_dir_path)
        while simulation != None:
            predictions = model.predictions(self.places, user)
            last_answer = simulation.last_answer
            out_svg = os.path.join(dest_dir_path, "step_" + str(last_answer['inserted']) + ".svg")
            asked_place = list(self.places[self.places['id'] == last_answer['place.asked']]['code'])[0].upper()
            asked_place_color = 'rgb(66, 184, 66)'
            if last_answer['place.asked'] != last_answer['place.answered']:
                asked_place_color = 'rgb(184, 66, 66)'
            optional_css = '.states[iso_a2=' + asked_place + '] { fill: \'' + asked_place_color + '\'; stroke: \'rgb(0, 0, 255)\'; stroke-width: 3; }\n'
            self._save(
                predictions,
                self._config_world(),
                out_svg,
                out_svg + '.css',
                color_spectrum = self._color_rgspectrum,
                optional_css = optional_css)
            simulation = simulation.step()

    def success_probability(self, out_svg):
        data = []
        for place in self.answers['place.asked'].unique():
            place_code = self.places[self.places['id'] == place].head()['code']
            place_code = list(place_code)[0]
            place_data = self.answers[self.answers['place.asked'] == place]
            success = place_data['place.asked'] == place_data['place.answered']
            data.append({
                'code'  : place_code,
                'ratio' : float(sum(success)) / len(place_data)})
        self._save(
            pd.DataFrame(data),
            self._config_world(),
            out_svg,
            out_svg + ".css")

    # data - code, ratio
    def _save(self, data, config, out_svg, out_css, color_spectrum = None, optional_css = None):
        if not color_spectrum:
            color_spectrum = self._color_bwspectrum
        write_data = data
        r_max = data['ratio'].max()
        r_min = data['ratio'].min()
        if r_min != r_max:
            write_data['ratio'] = data['ratio'].map(
                lambda x: (x - r_min) / (r_max - r_min))
        else:
            write_data['ratio'] = data['ratio'].map(
                lambda x: 0.5)
        self._create_css(write_data, out_css, color_spectrum, optional_css)
        css = open(out_css)
        self.kartograph.generate(
            config,
            outfile = out_svg,
            stylesheet = css.read())

    def _config_world(self):
        layer = {
            'src'   : self.shapefile,
            'class' : 'states'
        }
        return {'layers' : [layer]}

    def _create_css(self, data, filename, color_spectrum, optional_css):
        try:
            file = open(filename, 'w')
            r_median = data['ratio'].median()
            for i, row in data.iterrows():
                code = row['code'].upper()
                ratio = row['ratio']
                file.write('.states[iso_a2=' + code + '] { fill: ' + color_spectrum(ratio, r_median) + '; }\n')
            if optional_css:
                file.write(optional_css)
            file.close()
        finally:
            pass

    def _color_rgspectrum(self, val, median = 0.5): # val 0..1
        if val < 0 or val > 1:
            raise Exceptiion("The value has to be from [0,1] interval.")
        (r,g,b) = hsv_to_rgb(0.37 * val,1,1)
        (r,g,b) = map(lambda x: int(255*x), (r,g,b))
        return "'rgb("+`r`+','+`g`+','+`b`+")'"

    def _color_bwspectrum(self, val, median = 0.5): # val 0..1
        if val < 0 or val > 1:
            raise Exceptiion("The value has to be from [0,1] interval.")
        if median > 0.7:
            val = val ** 2
        elif median < 0.3:
            val = math.sqrt(val)
        r = int(255 * val)
        g = int(255 * val)
        b = int(255 * val)
        return "'rgb("+`r`+','+`g`+','+`b`+")'"

