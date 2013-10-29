import sys
sys.path.append("libs")

import geodata

answers = geodata.Answers.from_json("./target/data/answers.json")
places = geodata.Places.from_json("./target/data/places.json")
print "### processing", len(answers.data), "answers"
answers.to_csv("./target/data/answers.csv")
print "### processing", len(places.data), "places"
places.to_csv("./target/data/places.csv")
