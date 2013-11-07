import sys
from pprint import pprint

sys.path.append('../libs')
sys.path.append('../target/external-libs/')

import geodata
import kartograph

answers = geodata.Answers.from_csv('../target/data/answers.csv')
places = geodata.Places.from_csv('../target/data/places.csv')


analysis = geodata.MapAnalysis(
    kartograph = kartograph.Kartograph(),
    answers = answers,
    places = places,
    shapefile = '../target/data/world.shp')

analysis.success_probability('../target/maps/success_prob_all.svg')
analysis[analysis['type'] == 10].success_probability(
    '../target/maps/success_prob_open.svg')

simulator = geodata.Simulator(answers)
hierarchical_elo = geodata.HierarchicalElo()
baseline1 = geodata.ConstantModel(1)
baseline0 = geodata.ConstantModel(0)
simulated = simulator.simulate(hierarchical_elo)
print simulator.simulate(baseline0)
print simulator.simulate(baseline1)
print simulated
analysis.difficulties_from_model(
    simulated.model,
    '../target/maps/hierarchical_elo_difficulties.svg')
