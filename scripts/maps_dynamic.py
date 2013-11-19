import sys
from pprint import pprint

sys.path.append('../libs')
sys.path.append('../target/external-libs/')

import proso.geodata as geodata
import kartograph

answers = geodata.Answers.from_csv('../target/data/answers.csv')
places = geodata.Places.from_csv('../target/data/places.csv')

analysis = geodata.MapAnalysis(
    kartograph = kartograph.Kartograph(),
    answers = answers,
    places = places,
    shapefile = '../target/data/world.shp')


hierarchical_elo = geodata.HierarchicalElo()
analysis.model_seq_for_user(hierarchical_elo, 62, '../target/maps/dynamic')
