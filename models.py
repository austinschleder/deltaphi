"""
Create classes necessary for the fantasy simulator:
Player, Roster, League, Matchup, Season
"""

import numpy as np
import pandas as pd
import random

class Player:
    'Player description'

    def __init__(self, name, slot, scoring_array):
        gp = len(scoring_array)
        self.name = name
        self.position = slot[:2]
        self.slot = slot
        self.scoring_array = scoring_array
        self.gp = gp
        self.points = sum(scoring_array)
        self.points_per_game = sum(scoring_array)/gp
        self.points_per_week = sum(scoring_array)/16.0
        self.utility = get_certainty_equivalent(scoring_array)
        self.scoring_output = []
        self.final_rankings = []

    def get_random_score(self):
        random_score = random.choice(self.scoring_array)
        self.scoring_output.append(random_score)
        return random_score

def get_certainty_equivalent(scoring_array):
    gp = len(scoring_array)
    ce = np.expm1(sum(np.log1p(scoring_array))/gp)
    return ce

class Roster:
    'Roster description'

    def __init__(self, player_array):
        self.player_array = player_array
        self.player_names = [p.name for p in player_array]
        self.exp_points_per_week = sum([p.points_per_game for p in player_array])
        self.points_per_week = 0
        self.scoring_output = []
        self.scoring_breakdown = []
        self.win_expectancies = []
        self.final_rankings = []

    def get_position(self, position, cap=None):
        player_array = self.player_array
        cap = cap if cap else len(player_array)
        position_players = [player for player in player_array if player.position == position][:cap]
        return position_players

    def get_slot(self, slot, cap=None):
        player_array = self.player_array
        cap = cap if cap else len(player_array)
        slot_players = [player for player in player_array if player.slot == slot][:cap]
        return slot_players

    def get_random_scores(self):
        random_scores = [x.get_random_score() for x in self.player_array]
        self.scoring_output.append(sum(random_scores))
        self.scoring_breakdown.append(random_scores)
        return random_scores

class League:
    'League description'

    def __init__(self, roster_array, scoring_settings, league_size):
        self.roster_array = roster_array
        self.scoring_settings = scoring_settings
        self.league_size = league_size
        self.player_names = [r.player_names for r in roster_array]
        self.points_per_week = []
        self.win_pct = []
        self.final_rankings = []

    def simulate_week(self):
        roster_array = self.roster_array
        player_scores = [roster.get_random_scores() for roster in roster_array]
        roster_scores = [sum(x) for x in player_scores]
        self.analyze_week(roster_scores)

    def analyze_week(self, roster_scores):
        outscored = [sum([1.0 for x in roster_scores if x < rs]) for rs in roster_scores]
        expected_wins = [o / (self.league_size - 1) for o in outscored]
        self.append_expected_wins(expected_wins)

    def append_expected_wins(self, expected_wins):
        for i in xrange(self.league_size):
            self.roster_array[i].win_expectancies.append(expected_wins[i])

    def simulate_season(self, num_weeks):
        roster_array = self.roster_array
        for n in xrange(num_weeks):
            self.simulate_week()
        points_per_week = [sum(r.scoring_output)/num_weeks for r in roster_array]
        win_pct = [sum(r.win_expectancies)/num_weeks for r in roster_array]
        final_rankings = [sum([1.0 for x in win_pct if x >= fs]) for fs in win_pct]
        self.points_per_week, self.win_pct, self.final_rankings = points_per_week, win_pct, final_rankings
        for t in xrange(len(roster_array)):
            rank = final_rankings[t]
            roster_array[t].final_rankings.append(rank)
            roster_array[t].points_per_week = points_per_week[t]
            for p in roster_array[t].player_array:
                p.final_rankings.append(rank)



