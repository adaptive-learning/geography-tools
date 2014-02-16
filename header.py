# -*- coding: utf-8 -*-
import sys
sys.path.append("libs")

import matplotlib.pyplot as plt
import pandas as pd
import proso.geodata

answers = proso.geodata.load_csv("./target/data/geography.answer.csv");
