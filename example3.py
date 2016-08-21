from __future__ import print_function
import models3 as fs
import pandas as pd
import numpy as np

#LEAGUE_SIZE = 10
#ROSTER_POSITIONS = ['qb', 'rb', 'wr', 'te']
#ROSTER_SLOTS = ['qb1', 'rb1', 'rb2', 'wr1', 'wr2', 'wr3', 'te1']
#MINIMUM_GAMES_PLAYED = 0
#SEASON_LENGTH = 16
LEAGUE_SIZE = 4
ROSTER_POSITIONS = ['qb']
ROSTER_SLOTS = ['qb1', 'qb2']
SCORING_CATEGORIES = ['pass_yards', 'pass_tds', 'pass_ints', 'rush_yards', 'rush_tds', 'recs', 'rec_yards', 'rec_tds']
SCORING_VALUES = [0.05, 6.0, -2.0, 0.1, 6.0, 0.0, 0.1, 6.0]
MINIMUM_GAMES_PLAYED = 0
SEASON_LENGTH = 5
NUM_SEASONS = 3
NICKNAMES = ['Raiders', 'Seahawks', 'Colts', 'Chiefs', 'Chargers', 'Broncos', 'Cardinals', 'Packers', 'Bills', 'Rams', 'Bears', 'Falcons']

gl = pd.read_csv('2015_nfl_weekly_stats.csv')
gl['position'] = np.where(gl['position'] == 10.0, 'qb', np.where(gl['position'] == 20.0, 'rb', np.where(gl['position'] == 30.0, 'wr', np.where(gl['position'] == 40.0, 'te', 'other'))))
GAME_LOGS = gl

## Create Player_DB
player_db = fs.Player_DB(gl, SCORING_CATEGORIES, SCORING_VALUES)
player_db.set_tiers(ROSTER_POSITIONS, LEAGUE_SIZE, MINIMUM_GAMES_PLAYED)
print(player_db)

## Create a League
players = player_db.get_player_pool(ROSTER_SLOTS)
teams = fs.create_teams(LEAGUE_SIZE, NICKNAMES)
seasons = fs.create_seasons(NUM_SEASONS, SEASON_LENGTH)
league1 = fs.League(players, teams, seasons, ROSTER_SLOTS, SEASON_LENGTH)
print(league1)
print(league1.get_player_by_id('P090'))
[t.print_scoring_output() for t in league1.teams]
print(league1.get_season_by_id('S0002').team_rankings)

print(fs.numpy_rank([50, 30, 20, 40]))

#[print(p) for p in sorted(league1.get_position_players('qb'), key=lambda x: x.position_rank)]
#[print(t) for t in league1.teams[:5]]

#qb1s = player_db.get_position_tier('qb1', LEAGUE_SIZE, MINIMUM_GAMES_PLAYED)
#[print(qb) for qb in qb1s]