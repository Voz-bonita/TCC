import pandas as pd
import numpy as np


betting_sites = [
    "PointsBet",
    "BetMGM",
    "Caesars NJ Sportsbook",
    "FanDuel NJ Sportsbook",
    "DraftKings NJ Sportsbook",
    "BetRivers NY Sportsbook",
    "BetRivers NJ Sportsbook (1)",
    "UnibetNJ Sportsbook",
]
outcomes = ["Home", "Away", "Draw"]

names = zip(
    np.repeat(betting_sites, len(outcomes)), np.tile(outcomes, len(betting_sites))
)
names_concat = list(map(lambda x: f"{x[0]} | {x[1]}", names))

df = pd.read_csv("scrapping/data.csv")
df.columns = names_concat
df.to_csv("scrapping/data.csv", index=False, header=True, mode="w")
