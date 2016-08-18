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
        self.rosters = self.create_rosters(self.player_db, self.roster_slots)
        [self.team_array[t].set_roster(self.rosters[t]) for t in xrange(self.league_size)]

    def create_player_db(self):
        scoring_vector = np.asarray(self.scoring_settings)
        gl = self.game_logs
        gl['points'] = gl[['pass_yards', 'pass_tds', 'pass_ints', 'rush_yards', 'rush_tds', 'recs', 'rec_yards', 'rec_tds']].dot(scoring_vector)
        gl = gl[['player', 'position', 'points']]
        pdb = gl.groupby(['player', 'position'], as_index=False)['points'].apply(list).reset_index(name='scoring_array')
        player_array = [Player(pdb['player'][p], pdb['position'][p], pdb['scoring_array'][p]) for p in xrange(len(pdb))]
        return Player_DB(player_array)

    def create_teams(self, nicknames):
        team_array = [self.Team(nicknames[t]) for t in xrange(self.league_size)]
        return team_array

    def create_rosters(self, player_database, roster_slots):
        pdb = player_database
        league_size = self.league_size
        player_pool = []
        for slot in roster_slots:
            subset = pdb.get_position_tier(slot, league_size)
            random.shuffle(subset)
            player_pool.append(subset)
        player_pool_inverse = np.asarray(player_pool).T.tolist()
        rosters = [Roster(player_pool_inverse[t]) for t in xrange(league_size)]
        return rosters

class Team:
    'Team description'

    def __init__(self, nickname):
        self.nickname = nickname
        self.roster = None

    def __str__(self):
        return '{}: {} -- {}'.format(self.__class__.__name__, self.nickname, self.roster)

    def set_roster(self, roster):
        self.roster = roster

class Player:
    'Player description'

    def __init__(self, name, position, scoring_array):
        self.name = name
        self.position = position
        self.scoring_array = scoring_array
        self.gp = len(scoring_array)
        self.points_per_gp = sum(scoring_array)/len(scoring_array)
        self.utility = get_certainty_equivalent(scoring_array)
        self.consistency = self.utility/self.points_per_gp

    def __str__(self):
        return '{}: {} ({}) - {:.2f}/{:.2f}/{:.2f}'.format(self.__class__.__name__, self.name, self.position, self.points_per_gp, self.utility, self.consistency)

class Player_DB:
    'Player Database description'

    def __init__(self, player_array):
        self.database = player_array

    def __str__(self):
        return '{}: {} players'.format(self.__class__.__name__, len(self.database))

    def get_position_tier(self, slot, league_size):
        pdb = self.database
        pos, tier = convert_slot_to_position(slot)
        tier_start = (tier-1)*league_size
        tier_end = (tier)*league_size
        position_players = [p for p in pdb if p.position == pos]
        position_players.sort(key=lambda x: x.points_per_gp, reverse=True)
        position_tier = position_players[tier_start:tier_end]
        return position_tier

class Season:
    'Season description'

    def __init__(self, league_size, roster_slots, season_length):
        self.league_size = league_size
        self.roster_slots = roster_slots
        self.season_length = season_length

    def create_rosters(self, player_database, roster_slots, league_size):
        pdb = player_database
        player_pool = []
        for slot in roster_slots:
            subset = pdb.get_position_tier(slot, league_size)
            random.shuffle(subset)
            player_pool.append(subset)
        player_pool_inverse = np.asarray(player_pool).T.tolist()
        rosters = [Roster(player_pool_inverse[t]) for t in xrange(league_size)]
        return rosters

class Roster:
    'Roster description'

    def __init__(self, player_array):
        self.player_array = player_array

    def __str__(self):
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

def convert_slot_to_position(slot):
    position = slot[:2]
    tier = int(slot[2:])
    return position, tier 

def convert_position_to_slot(position, tier):
    slot = position + str(tier)
    return slot
