from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import options
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.wait import WebDriverWait
from datetime import datetime
import selenium
import json
import time
import sys
import os


def chunk_list(lst, n):
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def clean_odds_simple(match_id, clean_data, full_odds, market):
    if market == "both_score":
        names = ["yes", "no"]
    elif market == "h2h":
        names = ["home", "draw", "away"]

    clean_data[match_id][market] = {}

    try:
        for period in full_odds["periods"]:
            if period["name"] == "Fim do Jogo":
                odds = period["odds"]
                break
    except KeyError:
        return

    for odd in odds:
        clean_data[match_id][market][odd["bookie_name"]] = {
            n[i]: odd[f"o{i+1}"] for i, n in enumerate(names)
        }


def clean_odds(match_id, clean_data, full_odds, market):
    if market == "over/under":
        names = ["over", "under"]
    elif "spread" in market:
        names = ["home", "away"]
    elif market == "exact":
        names = ["odd"]

    try:
        for period in full_odds["periods"]:
            if period["name"] == "Fim do Jogo":
                divisions = period["odds"]
                break
    except KeyError:
        return

    odds_all = [*divisions["alternative"], *divisions["main"]]
    for odds_list_item in odds_all:
        clean_data[match_id][market][odds_list_item["name"]] = {}
        for _id, odd in odds_list_item["odds"].items():
            clean_data[match_id][market][odds_list_item["name"]][odd["bookie_name"]] = {
                n[i]: odd[f"o{i+1}"] for i, n in enumerate(names)
            }

    return


def scrape_odds(
    match_id: str,
    market: str,
    clean_data: dict,
    driver: webdriver,
) -> dict:
    IDS = {
        1: "h2h",
        3: "spread_asian",
        4: "over/under",
        6: "spread",
        8: "exact",
        11: "both_score",
    }
    IDS_REV = {v: k for k, v in IDS.items()}
    BASE_URL = "https://oddspedia.com/api/v1/getMatchOdds?wettsteuer=0&geoCode=BR&bookmakerGeoCode=BR&bookmakerGeoState=&matchId={match_id}&oddGroupId={odds_market}&inplay=0&language=br".format

    if market in clean_data[match_id]:
        return
    clean_data[match_id][market] = {}

    driver.get(BASE_URL(match_id=match_id, odds_market=IDS_REV[market]))
    try:
        json_response = driver.find_element(By.TAG_NAME, "pre")
    except selenium.common.exceptions.NoSuchElementException:
        json_response = driver.find_element(By.TAG_NAME, "body")

    try:
        incomplete_data = json.loads(json_response.text)
    except json.JSONDecodeError:
        return
    try:
        market_data = {}
        for data in incomplete_data["data"]["prematch"]:
            if data["id"] == IDS_REV[market]:
                market_data = data
                break
        market_data["id"]
    except KeyError:
        return

    if market in ["both_score", "h2h"]:
        clean_odds_simple(match_id, clean_data, market_data, market)
    else:
        clean_odds(match_id, clean_data, market_data, market)

    return


def main():
    LEAGUES = os.listdir("./odds/")
    opt = options.Options()
    driver = webdriver.Chrome(options=opt)

    # Chunk by 1 and use only "Supercopa do Brasil" for debug
    LEAGUES_keep = chunk_list(LEAGUES, 1)[int(sys.argv[1])]

    for league in LEAGUES_keep:
        print(league)

        with open(f"./blank_odds/{league}", "r") as infile:
            odds_present = json.load(infile)
        for i, id_ in enumerate(odds_present):
            ms = ["h2h", "exact", "over/under", "spread_asian", "spread", "both_score"]
            for m in ms:
                scrape_odds(
                    match_id=id_, market=m, clean_data=odds_present, driver=driver
                )

        with open(f"odds/{league}", "w+") as outfile:
            json.dump(odds_present, outfile)


if __name__ == "__main__":
    main()
