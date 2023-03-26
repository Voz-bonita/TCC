import requests
import pandas as pd
import numpy as np
import os
import json
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio


def request_info(date_Ymd: str) -> dict:
    url = f"https://api.actionnetwork.com/web/v1/scoreboard/soccer?period=game&bookIds=15,30,76,75,123,69,68,972,71,247,79&date=20230325"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    }

    response = requests.get(url, headers=headers)

    return json.loads(response.text)


def odds_by_time(time: datetime.datetime, names: list, ids: dict) -> list:
    response = request_info(time.strftime("%Y%m%d"))
    server_time = time + datetime.timedelta(hours=3)
    odds_all = []
    for game in response["games"]:
        if game["start_time"][:19] != server_time.strftime("%Y-%m-%dT%H:%M:%S"):
            continue

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

        odds = np.empty(len(ids) * 3)
        odds[:] = np.nan
        for odd in game["odds"][2:]:
            i = ids[odd["book_id"]]
            odds[i * 3 : i * 3 + 3] = [odd["ml_away"], odd["ml_home"], odd["draw"]]
        odds = np.append(odds, [teams[0], teams[1], outcome])
        odds_all.append(odds)

    odds_df = pd.DataFrame(odds_all, columns=names)
    odds_df.to_csv(
        f'./scrapping/raw/{time.strftime("%Y-%m-%dT%H_%M_%S")}.csv', index=False
    )

    return odds_df


def datetimes_all(response: dict) -> list:
    date_times_all = []
    for game in response["games"]:
        game_date = datetime.datetime.strptime(
            game["start_time"][:19], "%Y-%m-%dT%H:%M:%S"
        )
        game_date_brasilia = game_date - datetime.timedelta(hours=3)
        date_times_all.append((game_date_brasilia))

    return date_times_all


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
    OUTCOMES = ["Away", "Home", "Draw"]

    NAMES_ZIP = zip(
        np.repeat(BETTING_BOOKS, len(OUTCOMES)), np.tile(OUTCOMES, len(BETTING_BOOKS))
    )
    NAMES_CONCAT = list(map(lambda x: f"{x[0]} | {x[1]}", NAMES_ZIP))
    NAMES_CONCAT.append("Away")
    NAMES_CONCAT.append("Home")
    NAMES_CONCAT.append("Outcome")

    today = datetime.datetime.now().strftime("%Y%m%d")
    response = request_info(today)
    date_times = datetimes_all(response)

    scheduler = AsyncIOScheduler()

    for dt in date_times:
        print(dt)
        scheduler.add_job(
            odds_by_time, "date", run_date=dt, args=(dt, NAMES_CONCAT, BOOK_ID_ORDER)
        )
        break

    scheduler.start()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    main()
