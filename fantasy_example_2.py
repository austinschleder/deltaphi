from __future__ import print_function
import fantasy_classes_2 as fc
import pandas as pd
import numpy as np

LEAGUE_SIZE = 4
ROSTER = ['qb1', 'rb1', 'wr1', 'te1']
SCORING_VALUES = [0.05, 6.0, -2.0, 0.1, 6.0, 0.0, 0.1, 6.0]
SEASON_LENGTH = 16
NICKNAMES = ['Raiders', 'Seahawks', 'Colts', 'Chiefs', 'Chargers', 'Broncos', 'Cardinals', 'Packers', 'Bills', 'Rams', 'Bears', 'Falcons']

gl = pd.read_csv('2015_nfl_weekly_stats.csv')
gl['position'] = np.where(gl['position'] == 10.0, 'qb', np.where(gl['position'] == 20.0, 'rb', np.where(gl['position'] == 30.0, 'wr', np.where(gl['position'] == 40.0, 'te', 'other'))))
GAME_LOGS = gl

league1 = fc.League(GAME_LOGS, LEAGUE_SIZE, ROSTER, SCORING_VALUES, SEASON_LENGTH, NICKNAMES)
print(league1.player_db)
[print(t) for t in league1.team_array]
#[print(p) for p in league1.player_db.get_players(5)]
#[print(r) for r in league1.rosters]

def show_consistency_breakdown():
	consistent_player = league1.Player('Consistent', 'ex', [10.0, 10.0, 10.0, 10.0])
	consistent_player.display_player_stats()
	neutral_player = league1.Player('Neutral', 'ex', [4.0, 8.0, 12.0, 16.0])
	neutral_player.display_player_stats()
	risky_player = league1.Player('Risky', 'ex', [0.0, 0.0, 20.0, 20.0])
	risky_player.display_player_stats()
#show_consistency_breakdown()

