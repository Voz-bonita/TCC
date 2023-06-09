import os
import json


for file in os.listdir("scrapping/odds/"):
    odds_final = {}
    with open(f"scrapping/odds/{file}", "r") as f:
        odds_by_game = json.load(f)
    league = file.replace(".json", "")

    for game in odds_by_game:
        odds_final[game] = {}
        for market in odds_by_game[game]:
            if market in ["h2h", "both_score"]:
                for bookie in odds_by_game[game][market]:
                    if bookie not in odds_final[game]:
                        odds_final[game][bookie] = {}
                    odds_final[game][bookie][market] = odds_by_game[game][market][
                        bookie
                    ]
            else:
                for possible_outcome in odds_by_game[game][market]:
                    for bookie in odds_by_game[game][market][possible_outcome]:
                        if bookie not in odds_final[game]:
                            odds_final[game][bookie] = {}
                        if market not in odds_final[game][bookie]:
                            odds_final[game][bookie][market] = {}
                        odds_final[game][bookie][market][
                            possible_outcome
                        ] = odds_by_game[game][market][possible_outcome][bookie]

    with open(f"scrapping/temp/{file}", "w+") as outfile:
        json.dump(odds_final, outfile)

odds_all = {}
for file in os.listdir("scrapping/temp/"):
    with open(f"scrapping/temp/{file}", "r") as f:
        odds_by_game = json.load(f)

    league = file.replace("-odds.json", "")
    odds_all[league] = odds_by_game

with open(f"scrapping/odds_all.json", "w+") as outfile:
    json.dump(odds_all, outfile)


info_final = {}
for file in os.listdir("scrapping/info/"):
    with open(f"scrapping/info/{file}", "r") as f:
        info_by_game = json.load(f)

    league = file.replace("-info.json", "")
    info_final[league] = info_by_game

with open(f"scrapping/info_all.json", "w+") as outfile:
    json.dump(info_final, outfile)
