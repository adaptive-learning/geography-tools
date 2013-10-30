import sys
sys.path.append("../libs")
sys.path.append("../target/external-libs/")

import geodata
import kartograph
analysis = geodata.MapAnalysis(
    kartograph.Kartograph(),
    "../target/data/answers.csv",
    "../target/data/places.csv",
    "../target/data/world.shp")

analysis.success_probability("../target/maps/success_prob.svg")
