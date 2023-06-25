from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import options
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.wait import WebDriverWait
from datetime import datetime
from dateutil.relativedelta import relativedelta
import selenium
import json
import time
import sys
import os


def chunk_list(lst, n):
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def scrape_league_ids(
    league: dict,
    driver: webdriver,
) -> dict:
    start_date = datetime.strptime("2019", "%Y")
    end_date = start_date + relativedelta(months=6)

    API_MATCH_LIST = "https://oddspedia.com/api/v1/getMatchList?excludeSpecialStatus=1&sortBy=default&perPageDefault=400&startDate={start_date}T03%3A00%3A00Z&endDate={end_date}T02%3A59%3A59Z&geoCode=BR&status=all&sport=futebol&popularLeaguesOnly=0&category={category}&league={alias}&round=&page=1&perPage=400&language=br".format
    all_matches = {}

    while start_date.year < 2023:
        time.sleep(1)
        driver.get(
            API_MATCH_LIST(
                start_date=datetime.strftime(
                    start_date - relativedelta(days=7), "%Y-%m-%d"
                ),
                end_date=datetime.strftime(
                    end_date + relativedelta(days=7), "%Y-%m-%d"
                ),
                category=league["category"],
                alias=league["alias"],
            )
        )
        try:
            json_response = driver.find_element(By.TAG_NAME, "pre")
        except selenium.common.exceptions.NoSuchElementException:
            json_response = driver.find_element(By.TAG_NAME, "body")

        current_matches = json.loads(json_response.text)

        for match in current_matches["data"]["matchList"]:
            all_matches[match["id"]] = {
                "home": match["ht"],
                "away": match["at"],
                "home_score": match["hscore"],
                "away_score": match["ascore"],
                "round": match["league_round_name"],
            }

        start_date += relativedelta(months=6)
        end_date += relativedelta(months=6)
    return all_matches


def clean_odds(match_id, clean_data, full_odds, market):
    if market == "over/under":
        names = ["over", "under"]
    elif "spread" in market:
        names = ["home", "away"]
    elif market == "exact":
        names = ["odd"]

    try:
        for period in full_odds[market]["periods"]:
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


def scrape_ids_odds(
    game_ids: dict,
    driver: webdriver,
) -> dict:
    clean_data = {}
    IDS = {1: "h2h", 3: "spread_asian", 4: "over/under", 6: "spread", 8: "exact"}
    MARKET_INDEX = {1: 0, 3: 2, 4: 1, 8: 7, 6: 8}
    BASE_URL = "https://oddspedia.com/api/v1/getMatchOdds?wettsteuer=0&geoCode=BR&bookmakerGeoCode=BR&bookmakerGeoState=&matchId={match_id}&oddGroupId={odds_market}&inplay=0&language=br".format

    for match_id in game_ids:
        match_odds = {}
        clean_data[match_id] = {}
        for market in IDS.keys():
            clean_data[match_id][IDS[market]] = {}
            driver.get(BASE_URL(match_id=match_id, odds_market=market))
            try:
                json_response = driver.find_element(By.TAG_NAME, "pre")
            except selenium.common.exceptions.NoSuchElementException:
                json_response = driver.find_element(By.TAG_NAME, "body")

            try:
                incomplete_data = json.loads(json_response.text)
            except json.JSONDecodeError:
                continue

            try:
                current_market_data = {}
                for data in incomplete_data["data"]["prematch"]:
                    if data["id"] == market:
                        current_market_data = data
                        break
                current_market_data["id"]

            except IndexError:
                continue
            except KeyError:
                continue
            match_odds[IDS[market]] = current_market_data

        try:
            for period in match_odds["h2h"]["periods"]:
                if period["name"] == "Fim do Jogo":
                    for odd in period["odds"]:
                        clean_data[match_id]["h2h"][odd["bookie_name"]] = {
                            "home": odd["o1"],
                            "draw": odd["o2"],
                            "away": odd["o3"],
                        }
                    break
        except KeyError:
            pass

        clean_odds(match_id, clean_data, match_odds, "over/under")
        clean_odds(match_id, clean_data, match_odds, "spread")
        clean_odds(match_id, clean_data, match_odds, "exact")
        clean_odds(match_id, clean_data, match_odds, "spread_asian")

    return clean_data


def main():
    with open("./base_info/collected.json", "r") as file:
        LEAGUES = json.load(file)

    API_BASE = "https://oddspedia.com/api/v1/getMatchOdds?wettsteuer=0&geoCode=BR&bookmakerGeoCode=BR&bookmakerGeoState=&language=br"

    opt = options.Options()
    driver = webdriver.Chrome(options=opt)

    for league in LEAGUES:
        print(league)
        ids_found = scrape_league_ids(LEAGUES[league], driver)
        odds_to_be_found = {i: {} for i in ids_found}

        with open(f"blank_odds/{league}-odds.json", "w+") as outfile:
            json.dump(odds_to_be_found, outfile)

        with open(f"info/{league}-info.json", "w+") as outfile:
            json.dump(ids_found, outfile)


if __name__ == "__main__":
    main()

# Brasileirao - Serie B - 2022
# Missing: Sport - PE x Vasco da Gama, Rodada 35

# Libertadores - 2021
# Missing: Bolivar La Paz x Montevideo Wanderers FC, Qualificação - Jogo 2


# sport_x_vasco_id = 5924867
# bolivar_x_wanderers_id = None
