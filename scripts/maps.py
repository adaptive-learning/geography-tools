import sys
from pprint import pprint

sys.path.append("../libs")
sys.path.append("../target/external-libs/")

import geodata
import kartograph
analysis = geodata.MapAnalysis(
    kartograph = kartograph.Kartograph(),
    answers_csv = "../target/data/answers.csv",
    places_csv = "../target/data/places.csv",
    shapefile = "../target/data/world.shp")

analysis.success_probability("../target/maps/success_prob_all.svg")
analysis[analysis['type'] == 10].success_probability('../target/maps/success_prob_open.svg')
