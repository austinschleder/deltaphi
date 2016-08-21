from __future__ import print_function
import models3 as fs
import pandas as pd
import numpy as np

LEAGUE_SIZE = 6
ROSTER_POSITIONS = ['qb', 'rb', 'wr', 'te']
ROSTER_SLOTS = ['qb1', 'rb1', 'rb2', 'wr1', 'wr2', 'wr3', 'te1']
MINIMUM_GAMES_PLAYED = 8
SEASON_LENGTH = 16
SCORING_CATEGORIES = ['pass_yards', 'pass_tds', 'pass_ints', 'rush_yards', 'rush_tds', 'recs', 'rec_yards', 'rec_tds']
SCORING_VALUES = [0.04, 6.0, -2.0, 0.1, 6.0, 0.0, 0.1, 6.0]
NUM_SEASONS = 1000
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
#[print(p) for p in league1.players[:]]
#[print(t) for t in league1.teams[:5]]
#[print(l) for l in league1.seasons[:5]]

#print('Points+Rank', np.corrcoef([p.points_per_gp for p in league1.players], [p.average_team_ranking[0] for p in league1.players])[0][1])
#print('Points+Champ', np.corrcoef([p.points_per_gp for p in league1.players], [p.champion_pct[0] for p in league1.players])[0][1])
#print('Utility+Rank', np.corrcoef([p.utility for p in league1.players], [p.average_team_ranking[0] for p in league1.players])[0][1])
#print('Utility+Champ', np.corrcoef([p.utility for p in league1.players], [p.champion_pct[0] for p in league1.players])[0][1])


[print(p) for p in sorted(league1.get_slot_players('qb1'), key=lambda x: x.average_team_ranking[0], reverse=True)]
[print(p) for p in sorted(league1.get_slot_players('rb1'), key=lambda x: x.average_team_ranking[0], reverse=True)]
[print(p) for p in sorted(league1.get_slot_players('rb2'), key=lambda x: x.average_team_ranking[0], reverse=True)]
[print(p) for p in sorted(league1.get_slot_players('wr1'), key=lambda x: x.average_team_ranking[0], reverse=True)]
[print(p) for p in sorted(league1.get_slot_players('wr2'), key=lambda x: x.average_team_ranking[0], reverse=True)]
[print(p) for p in sorted(league1.get_slot_players('wr3'), key=lambda x: x.average_team_ranking[0], reverse=True)]
[print(p) for p in sorted(league1.get_slot_players('te1'), key=lambda x: x.average_team_ranking[0], reverse=True)]


#[print(t) for t in league1.teams[:5]]

#qb1s = player_db.get_position_tier('qb1', LEAGUE_SIZE, MINIMUM_GAMES_PLAYED)
#[print(qb) for qb in qb1s]