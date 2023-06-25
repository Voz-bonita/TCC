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
