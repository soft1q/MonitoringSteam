import os
import logging
import time
import re
import unicodedata
import graphyte


from selenium import webdriver
from bs4 import BeautifulSoup

logging.getLogger().setLevel(logging.INFO)

BASE_URL = 'https://steamdb.info/graph/'

GAMES = {
    'Dota 2': 'dota',
    'Counter-Strike: Global Offensive': 'csgo',
    "PLAYERUNKNOWN'S BATTLEGROUNDS": 'pubg',
    'Grand Theft Auto V': 'gta',
    'Terraria': 'terraria'
}


def parse_steamdb_page(page):
    game_rows = page.findAll('tr', {'class': 'app'})

    games = []
    for row in game_rows:
        game_utf8 = row.findAll('a')[1].text
        game = unicodedata.normalize("NFKD", game_utf8)
        if game not in GAMES:
            continue
        curr_players = int(row.findAll('td')[4]['data-sort'])

        games.append((GAMES[game], curr_players))
    return games


GRAPHITE_HOST = 'graphite'


def send_metrics(games):
    sender = graphyte.Sender(GRAPHITE_HOST, prefix='games')
    for game in games:
        sender.send(game[0], game[1])


def main():

    driver = webdriver.Remote(
        command_executor='http://selenium:4444/wd/hub',
        desired_capabilities={'browserName': 'chrome', 'javascriptEnabled': True}
    )

    driver.get('https://steamdb.info/graph/')
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    metric = parse_steamdb_page(soup)
    send_metrics(metric)

    driver.quit()

    logging.info('Accessed %s ..', BASE_URL)
    logging.info('Page title: %s', driver.title)


if __name__ == '__main__':
    main()