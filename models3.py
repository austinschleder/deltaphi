"""
Create classes necessary for the fantasy simulator:
League, Player_DB, Player, Team, Roster, Season
"""

from __future__ import print_function
import numpy as np
import pandas as pd
import random

class League:
    """
    Serves as a container for all of the objects that are going to be created.
    Seasons: LEAGUE_LENGTH
    Teams: LEAGUE_SIZE
    Rosters: LEAGUE_LENGTH x LEAGUE SIZE (1 per Team*Season)
    Players: LEAGUE_SIZE x ROSTER_SIZE (1 per Team*Roster, repeated every season)
    """
    id = 1
    
    def __init__(self, players, teams, seasons):
        self.league_id = League.id
        League.id += 1
        self.players = players
        self.teams = teams
        self.seasons = seasons

    def __str__(self):
        return '{} {}: {} players, {} teams, {} seasons'.format(self.__class__.__name__, self.league_id, len(self.players), len(self.teams), len(self.seasons))

    def get_position_players(self, position):
        position_players = [p for p in self.players if p.position == position]
        return position_players

class Player_DB:
    """
    Holds every Player object.
    In addition to creating Players from game logs, it should have functions for
    sorting, filtering, and returning Players based on different attributes.
    """
    id = 1

    def __init__(self, game_logs, scoring_categories, scoring_values):
        self.db_id = Player_DB.id
        Player_DB.id += 1
        pdb = analyze_game_logs(game_logs, scoring_categories, scoring_values)
        self.players = create_players_from_pdb(pdb)
        self.has_tiers = False

    def __str__(self):
        return '{}: {} player(s)'.format(self.__class__.__name__, len(self.players))

    def get_position_tier(self, slot, league_size, minimum_games_played):
        pdb = self.players
        pos, tier = convert_slot_to_position(slot)
        tier_start = (tier-1)*league_size
        tier_end = (tier)*league_size
        position_players = [p for p in pdb if (p.position == pos) & (p.gp >= minimum_games_played)]
        position_players.sort(key=lambda x: x.points_per_gp, reverse=True)
        position_tier = position_players[tier_start:tier_end]
        [p.set_slot(slot) for p in position_tier]
        return position_tier

    def set_tiers(self, positions, league_size, minimum_games_played):
        pdb = self.players
        tier_size = league_size
        pdb = [p for p in pdb if p.gp >= minimum_games_played]
        for pos in positions:
            position_players = [p for p in pdb if p.position == pos]
            num_players = len(position_players)
            position_players.sort(key=lambda x: x.points_per_gp, reverse=True)
            tier_assignments = [(t+1)/tier_size + 1 for t in range(num_players)]
            slot_assignments = [convert_position_to_slot(pos, t) for t in tier_assignments]
            [position_players[i].set_slot(slot_assignments[i]) for i in range(num_players)]
            [position_players[i].set_position_rank(i+1) for i in range(num_players)]
        self.has_tiers = True

    def get_player_pool(self, roster_slots):
        if self.has_tiers:
            pdb = self.players
            player_pool = [p for p in pdb if p.slot in roster_slots]
            return player_pool
        else:
            print('Tiers have not been set yet.')

class Player:
    """
    Contains name, position, and scoring_array for a particular player.
    Persists throughout league, reassigned to new roster/team every season.
    Should it contain slot/tier information (AKA 'rb' versus 'rb1')?
    Should it store results (Player.scoring_output[season][week]) or does that go somewhere else?
    """
    id = 1

    def __init__(self, name, position, scoring_array):
        self.player_id = Player.id
        Player.id += 1
        self.name = name
        self.position = position
        self.scoring_array = scoring_array
        self.points = sum(scoring_array)
        self.gp = len(scoring_array)
        self.points_per_gp = sum(scoring_array)/len(scoring_array)
        self.utility = get_certainty_equivalent(scoring_array)
        self.consistency = self.utility/self.points_per_gp
        self.slot = position
        self.position_rank = 0

    def __str__(self):
        return '{} {:3d}: {:20s} ({}) -- {:.2f} = {:4.2f} / {:4.2f}'.format(self.__class__.__name__, self.player_id, self.name, self.slot, self.consistency, self.utility, self.points_per_gp)

    def set_slot(self, slot):
        self.slot = slot

    def set_position_rank(self, position_rank):
        self.position_rank = position_rank

class Team:
    """
    Contains team nickname.
    Persists throughout league, reassigned new roster/players every season.
    Should it store results (Player.scoring_output[season][week]) or does that go somewhere else?
    """
    id = 1

    def __init__(self, nickname):
        self.team_id = Team.id
        Team.id += 1
        self.nickname = nickname

    def __str__(self):
        return '{} {}: {}'.format(self.__class__.__name__, self.team_id, self.nickname)

class Season:
    """
    Contains final standings and team rank.
    """
    id = 1

    def __init__(self):
        self.season_id = Season.id
        Season.id += 1

###############
## Functions ##
###############

def analyze_game_logs(game_logs, scoring_categories, scoring_values):
    game_logs['points'] = game_logs[scoring_categories].dot(scoring_values)
    gl = game_logs[['player', 'position', 'points']]
    pdb = gl.groupby(['player', 'position'], as_index=False)['points'].apply(list).reset_index(name='scoring_array')
    return pdb

def create_players_from_pdb(pdb):
    players = [Player(pdb['player'][p], pdb['position'][p], pdb['scoring_array'][p]) for p in xrange(len(pdb))]
    return players

def create_teams(league_size, nicknames):
    teams = [Team(nicknames[t]) for t in xrange(league_size)]
    return teams

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
