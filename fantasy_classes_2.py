"""
Create classes necessary for the fantasy simulator:
League, Team, Player, Season, Roster
"""

from __future__ import print_function
import numpy as np
import pandas as pd
import random

class League:
    'League description'

    def __init__(self, game_logs, league_size, roster_slots, scoring_settings, season_length, nicknames):
        self.game_logs = game_logs
        self.league_size = league_size
        self.roster_slots = roster_slots
        self.scoring_settings = scoring_settings
        self.season_length = season_length
        
        self.player_db = self.create_player_db()
        self.team_array = self.create_teams(nicknames)
        self.rosters = self.create_rosters(self.player_db.database)
        [self.team_array[t].set_roster(self.rosters[t]) for t in xrange(league_size)]

    def create_player_db(self):
        scoring_vector = np.asarray(self.scoring_settings)
        gl = self.game_logs
        gl['points'] = gl[['pass_yards', 'pass_tds', 'pass_ints', 'rush_yards', 'rush_tds', 'recs', 'rec_yards', 'rec_tds']].dot(scoring_vector)
        gl = gl[['player', 'position', 'points']]
        pdb = gl.groupby(['player', 'position'], as_index=False)['points'].apply(list).reset_index(name='scoring_array')
        player_array = [self.Player(pdb['player'][p], pdb['position'][p], pdb['scoring_array'][p]) for p in xrange(len(pdb))]
        return self.Player_DB(player_array)

    def create_teams(self, nicknames):
        team_array = [self.Team(nicknames[t]) for t in xrange(self.league_size)]
        return team_array

    def create_rosters(self, player_database):
        pdb = player_database
        roster_positions = ['qb', 'rb', 'wr', 'te']
        position_rankings = []
        for pos in roster_positions:
            subset = [p for p in pdb if p.slot == pos]
            subset.sort(key=lambda x: x.points_per_gp, reverse=True)
            position_rankings.append(subset)
        return self.randomize_assignments(position_rankings, self.league_size)

    def randomize_assignments(self, position_rankings, league_size):
        starts = [0, league_size, 2*league_size]
        ends = [league_size, 2*league_size, 3*league_size]
        qb1s = position_rankings[0][starts[0]:ends[0]]
        rb1s = position_rankings[1][starts[0]:ends[0]]
        rb2s = position_rankings[1][starts[1]:ends[1]]
        wr1s = position_rankings[2][starts[0]:ends[0]]
        wr2s = position_rankings[2][starts[1]:ends[1]]
        wr3s = position_rankings[2][starts[2]:ends[2]]
        te1s = position_rankings[3][starts[0]:ends[0]]
        random.shuffle(qb1s)
        random.shuffle(rb1s)
        random.shuffle(rb2s)
        random.shuffle(wr1s)
        random.shuffle(wr2s)
        random.shuffle(wr3s)
        random.shuffle(te1s)
        rosters = [self.Roster([qb1s[t], rb1s[t], rb2s[t], wr1s[t], wr2s[t], wr3s[t], te1s[t]]) for t in xrange(league_size)]
        return rosters

    class Team:
        'Team description'

        def __init__(self, nickname):
            self.nickname = nickname
            self.roster = None

        def __repr__(self):
            return '{}: {} -- {}'.format(self.__class__.__name__, self.nickname, self.roster)

        def set_roster(self, roster):
            self.roster = roster

    class Player:
        'Player description'

        def __init__(self, name, slot, scoring_array):
            self.name = name
            self.slot = slot
            self.scoring_array = scoring_array
            self.gp = len(scoring_array)
            self.points_per_gp = sum(scoring_array)/len(scoring_array)
            self.utility = get_certainty_equivalent(scoring_array)
            self.consistency = self.utility/self.points_per_gp

        def __repr__(self):
            return '{}: {} ({}) - {:.2f}/{:.2f}/{:.2f}'.format(self.__class__.__name__, self.name, self.slot, self.points_per_gp, self.utility, self.consistency)

    class Player_DB:
        'Player Database description'

        def __init__(self, player_array):
            self.database = player_array

        def __repr__(self):
            return '{}: {} players'.format(self.__class__.__name__, len(self.database))

        def get_players(self, num_players):
            return self.database[:num_players]

        def print_player_info(self, num_players):
            [print(p) for p in self.database[:num_players]]

    class Roster:
        'Roster description'

        def __init__(self, player_array):
            self.player_array = player_array

        def __repr__(self):
            s = self.player_array
            return 'qb1: {}; rb1: {}; rb2: {}; wr1: {}; wr2: {}; wr3: {}; te1: {}'.format(s[0], s[1], s[2], s[3], s[4], s[5], s[6])


######################
## Helper Functions ##
######################

def get_certainty_equivalent(scoring_array):
    'Used in Player class to evaluate consistency'
    gp = len(scoring_array)
    ce = np.expm1(sum(np.log1p(scoring_array))/gp)
    return ce
