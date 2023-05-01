import requests
import pandas as pd
import numpy as np
import json
import datetime
import time


def request_info(date_Ymd: str) -> dict:
    url = f"https://api.actionnetwork.com/web/v1/scoreboard/soccer?period=game&bookIds=15,30,76,75,123,69,68,972,71,247,79&date={date_Ymd}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    }

    response = requests.get(url, headers=headers)

    return json.loads(response.text)


def odds_by_time(Ymd: str, names: list, ids: dict) -> list:
    response = request_info(Ymd)

    odds_all = []
    for game in response["games"]:
        league = game["league_name"]
        free = game["is_free"]
        teams = [game["teams"][0]["full_name"], game["teams"][1]["full_name"]]
        first_is_away = game["teams"][0]["id"] == game["away_team_id"]
        if not first_is_away:
            teams = list(reversed(teams))

        outcome = np.nan
        if game["status"] == "complete":
            winner_id = game["winning_team_id"]
            if winner_id == game["away_team_id"]:
                outcome = 0
            elif winner_id == None:
                outcome = 1
            else:
                outcome = 2
        elif game["status"] == "postponed" or game["status"] == "scheduled":
            continue
        else:
            print(f"Something went wrong in {Ymd}")

        odds = np.empty(len(ids) * 17)
        odds[:] = np.nan

        try:
            odds_listed = game["odds"][2:]
        except KeyError:
            print(f"No odds for a game in {Ymd}")
            continue

        for odd in odds_listed:
            i = ids[odd["book_id"]]
            odds[i * 17 : i * 17 + 17] = [
                odd["ml_away"],
                odd["ml_home"],
                odd["draw"],
                odd["over"],
                odd["under"],
                odd["total"],
                odd["away_total"],
                odd["away_over"],
                odd["away_under"],
                odd["home_total"],
                odd["home_over"],
                odd["home_under"],
                odd["spread_away"],
                odd["spread_home"],
                odd["spread_away_line"],
                odd["spread_home_line"],
                odd["num_bets"],
            ]
        odds = np.append(odds, [teams[0], teams[1], outcome, league, free, Ymd])
        odds_all.append(odds)

    odds_df = pd.DataFrame(odds_all, columns=names)
    return odds_df


def main():
    BETTING_BOOKS = [
        "DraftKings NJ Sportsbook",
        "FanDuel NJ Sportsbook",
        "BetRivers NJ Sportsbook (1)",
        "BetMGM",
        "PointsBet",
        "bet365",
        "Caesars NJ Sportsbook",
        "UnibetNJ Sportsbook",
        "BetRivers NY Sportsbook",
    ]
    BOOK_ID = [68, 69, 71, 75, 76, 79, 123, 247, 972]
    BOOK_ID_ORDER = dict(zip(BOOK_ID, list(range(len(BOOK_ID)))))
    BETTING_DATA = [
        "Away",
        "Home",
        "Draw",
        "Over",
        "Under",
        "Total",
        "Away_Total",
        "Away_Over",
        "Away_Under",
        "Home_Total",
        "Home_Over",
        "Home_Under",
        "Spread_away",
        "Spread_home",
        "Spread_away_line",
        "Spread_home_line",
        "Num_Bets",
    ]

    NAMES_ZIP = zip(
        np.repeat(BETTING_BOOKS, len(BETTING_DATA)),
        np.tile(BETTING_DATA, len(BETTING_BOOKS)),
    )
    NAMES_CONCAT = list(map(lambda x: f"{x[0]} | {x[1]}", NAMES_ZIP))
    NAMES_CONCAT.append("Away")
    NAMES_CONCAT.append("Home")
    NAMES_CONCAT.append("Outcome")
    NAMES_CONCAT.append("League")
    NAMES_CONCAT.append("Free")
    NAMES_CONCAT.append("Ymd")

    full_data = pd.DataFrame(columns=NAMES_CONCAT)
    start = datetime.datetime.now()
    dates = [start - datetime.timedelta(days=i + 1) for i in range(365)]
    for date in dates:
        print(date.strftime("%Y%m%d"))
        current = date.strftime("%Y%m%d")
        odds_scrapped = odds_by_time(current, NAMES_CONCAT, BOOK_ID_ORDER)
        full_data = pd.concat([full_data, odds_scrapped])
        time.sleep(5)

    full_data.to_csv("./scrapping/raw/data.csv", index=False)


if __name__ == "__main__":
    main()
