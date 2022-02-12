import requests
import datetime
import json
import sqlite3

teams = {}

conn = sqlite3.connect('statistics.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS teams(
   name_id INTEGER PRIMARY KEY NOT NULL,
   name_team TEXT NOT NULL);""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS score(
   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
   date_game timestamp,
   away_team_id INT NOT NULL,
   away_score INT NOT NULL,
   home_team_id INT NOT NULL,
   home_score INT NOT NULL);""")
conn.commit()
cur.close()


def date_games():
    today = datetime.date.today()
    first_currentmonth = today.replace(day=1)
    lastmonth = first_currentmonth - datetime.timedelta(days=1)
    first_lastmonth = lastmonth.replace(day=1)
    start_day = first_lastmonth.strftime("%Y-%m-%d")
    end_day = lastmonth.strftime("%Y-%m-%d")
    return start_day, end_day


def parse_api():
    param = dict(
        teamId='19',
        startDate=date_games()[0],
        endDate=date_games()[1])
    url = "https://statsapi.web.nhl.com/api/v1/schedule?"
    reqs = requests.get(url, param)
    return reqs


todos = json.loads(parse_api().text)
games = todos['dates']
cur = conn.cursor()
for game in games:
    game_teams = game['games'][0]['teams']
    team_away = game_teams['away']
    team_home = game_teams['home']
    teams.update({team_away['team']['id']: team_away['team']['name']})
    teams.update({team_home['team']['id']: team_home['team']['name']})
    date_game = ('-'.join(game['games'][0]['gameDate'].split('T')[:-1]))
    away_team_id = team_away['team']['id']
    away_score = team_away['score']
    home_team_id = team_home['team']['id']
    home_score = team_home['score']

    cur.execute("""INSERT INTO score(
    date_game,
    away_team_id,
    away_score,
    home_team_id,
    home_score) VALUES (?, ?, ?, ?, ?)""", (
        date_game, away_team_id, away_score, home_team_id, home_score))
    conn.commit()

for team in teams.items():
    cur.execute("INSERT INTO teams('name_id', 'name_team') VALUES (?, ?)", (
        team[0], team[1]))
    conn.commit()

cur.close()
