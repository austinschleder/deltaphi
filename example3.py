from __future__ import print_function
import models3 as fs
import pandas as pd
import numpy as np

LEAGUE_SIZE = 10
MINIMUM_GAMES_PLAYED = 10
INJURY_HANDLING = 'zeros'
SEASON_LENGTH = 16
NUM_SEASONS = 1000

ROSTER_POSITIONS = ['qb', 'rb', 'wr', 'te']
ROSTER_SLOTS = ['qb1', 'rb1', 'rb2', 'wr1', 'wr2', 'wr3', 'te1']

SCORING_CATEGORIES = ['pass_yards', 'pass_tds', 'pass_ints', 'rush_yards', 'rush_tds', 'recs', 'rec_yards', 'rec_tds']
SCORING_VALUES = [0.04, 6.0, -2.0, 0.1, 6.0, 0.0, 0.1, 6.0]

NICKNAMES = ['Raiders', 'Seahawks', 'Colts', 'Chiefs', 'Chargers', 'Broncos', 'Cardinals', 'Packers', 'Bills', 'Rams', 'Bears', 'Falcons']

SAMPLE_SEASON = 2015

gl = pd.read_csv('{}_nfl_weekly_stats.csv'.format(SAMPLE_SEASON))
gl['position'] = np.where(gl['position'] == 10.0, 'qb', np.where(gl['position'] == 20.0, 'rb', np.where(gl['position'] == 30.0, 'wr', np.where(gl['position'] == 40.0, 'te', 'other'))))
GAME_LOGS = gl

## Create Player_DB
player_db = fs.Player_DB(gl, SCORING_CATEGORIES, SCORING_VALUES, SEASON_LENGTH, INJURY_HANDLING)
player_db.set_tiers(ROSTER_POSITIONS, LEAGUE_SIZE, MINIMUM_GAMES_PLAYED)
print(player_db)

## Create a League
players = player_db.get_player_pool(ROSTER_SLOTS)
teams = fs.create_teams(LEAGUE_SIZE, NICKNAMES)
seasons = fs.create_seasons(NUM_SEASONS, SEASON_LENGTH)
league1 = fs.League(players, teams, seasons, ROSTER_SLOTS, SEASON_LENGTH)
print(league1)

## Show players in each tier. Sorted by championship percentage, but can be changed to final ranking (arithmatic or harmonic mean)
if False:
	[print(p) for p in sorted(league1.get_slot_players('qb1'), key=lambda x: x.champion_pct[0], reverse=True)]
	print('--------------------------------------------------------------------------------------')
	[print(p) for p in sorted(league1.get_slot_players('rb1'), key=lambda x: x.champion_pct[0], reverse=True)]
	print('--------------------------------------------------------------------------------------')
	[print(p) for p in sorted(league1.get_slot_players('rb2'), key=lambda x: x.champion_pct[0], reverse=True)]
	print('--------------------------------------------------------------------------------------')
	[print(p) for p in sorted(league1.get_slot_players('wr1'), key=lambda x: x.champion_pct[0], reverse=True)]
	print('--------------------------------------------------------------------------------------')
	[print(p) for p in sorted(league1.get_slot_players('wr2'), key=lambda x: x.champion_pct[0], reverse=True)]
	print('--------------------------------------------------------------------------------------')
	[print(p) for p in sorted(league1.get_slot_players('wr3'), key=lambda x: x.champion_pct[0], reverse=True)]
	print('--------------------------------------------------------------------------------------')
	[print(p) for p in sorted(league1.get_slot_players('te1'), key=lambda x: x.champion_pct[0], reverse=True)]
	print('--------------------------------------------------------------------------------------')
	
## Show all players, sorted by championship percentage. Serves as overall rankings.
if True:
	[print(p) for p in sorted(league1.players, key=lambda x: x.champion_pct[0], reverse=True)]

## Check the correlation between inputs (points&utility) and outputs (team_rank&championship).
if False:
	print('Points+Rank', np.corrcoef([p.points_per_gp_normalized for p in league1.players], [5-p.average_team_ranking[0] for p in league1.players])[0][1])
	print('Points+Champ', np.corrcoef([p.points_per_gp_normalized for p in league1.players], [p.champion_pct[0] for p in league1.players])[0][1])
	print('Utility+Rank', np.corrcoef([p.utility_normalized for p in league1.players], [5-p.average_team_ranking[0] for p in league1.players])[0][1])
	print('Utility+Champ', np.corrcoef([p.utility_normalized for p in league1.players], [p.champion_pct[0] for p in league1.players])[0][1])