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
    
    def __init__(self, players, teams, seasons, roster_slots, season_length):
        self.league_id = 'L' + str(League.id).zfill(2)
        League.id += 1
        self.players = players
        self.teams = teams
        self.seasons = seasons
        self.roster_slots = roster_slots
        self.season_length = season_length

        self.set_rosters()
        self.generate_player_scores()
        self.calculate_team_scores()
        self.calculate_season_stats()

    def __str__(self):
        return '{} {}: {} players, {} teams, {} seasons'.format(self.__class__.__name__, self.league_id, len(self.players), len(self.teams), len(self.seasons))

    def get_player_by_id(self, player_id):
        return [p for p in self.players if p.player_id == player_id][0]

    def get_team_by_id(self, team_id):
        return [t for t in self.teams if t.team_id == team_id][0]

    def get_season_by_id(self, season_id):
        return [s for s in self.seasons if s.season_id == season_id][0]

    def get_position_players(self, position):
        position_players = [p for p in self.players if p.position == position]
        return position_players

    def set_rosters(self):
        seasons = self.seasons
        teams = self.teams
        players = self.players
        roster_slots = self.roster_slots
        for s in seasons:
            rosters = {t.team_id: [] for t in teams}
            num_teams = len(teams)
            for slot in roster_slots:
                slot_players = get_slot_players(players, slot)
                assignments = zip(teams, slot_players)
                [rosters[t.team_id].append(p.player_id) for t, p in assignments]
                [p.update_team_assignment(s.season_id, t.team_id) for t, p in assignments]
            s.rosters = rosters
            [t.update_player_assignments(s.season_id, rosters[t.team_id]) for t in teams]

    def generate_player_scores(self):
        seasons = self.seasons
        players = self.players
        for s in seasons:
            season_length = s.season_length
            for p in players:
                p.update_scoring_output(s.season_id, [random.choice(p.scoring_array) for i in xrange(season_length)])

    def calculate_team_scores(self):
        seasons = self.seasons
        teams = self.teams
        players = self.players
        for s in seasons:
            season_length = s.season_length
            for t in teams:
                weekly_output = [sum(p.scoring_output[s.season_id][i] for p in players if p.team_assignments[s.season_id] == t.team_id) for i in xrange(season_length)]
                t.update_scoring_output(s.season_id, weekly_output)

    def calculate_season_stats(self):
        seasons = self.seasons
        teams = self.teams
        for s in seasons:
            season_length = s.season_length
            league_size = len(teams)
            matchup_rankings_by_week = [numpy_rank([t.scoring_output[s.season_id][i] for t in teams]) for i in xrange(season_length)]
            matchup_rankings_by_team = map(list, zip(*matchup_rankings_by_week))
            [s.update_team_rankings_weekly(teams[i].team_id, matchup_rankings_by_team[i]) for i in xrange(league_size)]


class Player_DB:
    """
    Holds every Player object.
    In addition to creating Players from game logs, it should have functions for
    sorting, filtering, and returning Players based on different attributes.
    """
    id = 1

    def __init__(self, game_logs, scoring_categories, scoring_values):
        self.db_id = 'DB' + str(Player_DB.id)
        Player_DB.id += 1
        pdb = analyze_game_logs(game_logs, scoring_categories, scoring_values)
        self.players = create_players_from_pdb(pdb)
        self.has_tiers = False

    def __str__(self):
        return '{}: {} player(s)'.format(self.__class__.__name__, len(self.players))

    def set_tiers(self, positions, league_size, minimum_games_played):
        pdb = self.players
        pdb_qualified = [p for p in pdb if p.gp >= minimum_games_played]
        for pos in positions:
            position_players = [p for p in pdb_qualified if p.position == pos]
            position_players_ranked = sort_array_descending(position_players, 'points_per_gp')
            set_position_tiers(position_players_ranked, pos, league_size)
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
        self.player_id = 'P' + str(Player.id).zfill(3)
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
        self.scoring_output = {}
        self.team_assignments = {}

    def __str__(self):
        return '{} {}: {:20s} ({}) -- {:.2f} = {:5.2f} / {:5.2f} -- {}'.format(self.__class__.__name__, self.player_id, self.name, self.slot, self.consistency, self.utility, self.points_per_gp, self.team_assignments)

    def set_slot(self, slot):
        self.slot = slot

    def set_position_rank(self, position_rank):
        self.position_rank = position_rank

    def update_team_assignment(self, season_id, team_id):
        self.team_assignments.update({season_id: team_id})

    def update_scoring_output(self, season_id, seasonal_scoring):
        self.scoring_output.update({season_id: seasonal_scoring})

class Team:
    """
    Contains team nickname.
    Persists throughout league, reassigned new roster/players every season.
    Should it store results (Player.scoring_output[season][week]) or does that go somewhere else?
    """
    id = 1

    def __init__(self, nickname):
        self.team_id = 'T' + str(Team.id).zfill(2)
        Team.id += 1
        self.nickname = nickname
        self.player_assignments = {}
        self.scoring_output = {}

    def __str__(self):
        return '{} {}: {} -- {}'.format(self.__class__.__name__, self.team_id, self.nickname, self.scoring_output)

    def update_player_assignments(self, season_id, roster):
        self.player_assignments.update({season_id: roster})

    def update_scoring_output(self, season_id, seasonal_scoring):
        self.scoring_output.update({season_id: seasonal_scoring})

    def print_scoring_output(self):
        print(self.team_id, ' '.join([str(x) for x in self.scoring_output['S0002']]))

class Season:
    """
    Contains final standings and team rank.
    """
    id = 1

    def __init__(self, season_length):
        self.season_id = 'S' + str(Season.id).zfill(4)
        Season.id += 1
        self.season_length = season_length
        self.rosters = {}
        self.team_rankings = {}

    def __str__(self):
        return '{} {}: {} teams'.format(self.__class__.__name__, self.season_id, len(self.rosters))

    def set_rosters(self, teams, players, roster_slots):
        rosters = {t.team_id: [] for t in teams}
        num_teams = len(teams)
        for slot in roster_slots:
            slot_players = [p for p in players if p.slot == slot]
            random.shuffle(slot_players)
            assignments = zip(teams, slot_players)
            [rosters[t.team_id].append(p.player_id) for t, p in assignments]
            [p.update_team_assignment(self.season_id, t.team_id) for t, p in assignments]
        return rosters

    def generate_player_scores(self, players):
        season_length = self.season_length
        season_id = self.season_id
        [p.update_scoring_output(season_id, [random.choice(p.scoring_array) for i in xrange(season_length)]) for p in players]

    def update_team_rankings_weekly(self, team_id, matchup_rankings_by_team):
        self.team_rankings.update({team_id: matchup_rankings_by_team})

    def print_team_rankings(self):
        [print(' '.join([str(x) for x in self.team_rankings[i]])) for i in ['T01', 'T02', 'T03', 'T04']]

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

def create_seasons(num_seasons, season_length):
    seasons = [Season(season_length) for i in xrange(num_seasons)]
    return seasons

def set_position_tiers(players, position, league_size):
    num_players = len(players)
    tier_assignments = [t/league_size + 1 for t in range(num_players)]
    slot_assignments = [convert_position_to_slot(position, t) for t in tier_assignments]
    [players[i].set_slot(slot_assignments[i]) for i in range(num_players)]
    [players[i].set_position_rank(i+1) for i in range(num_players)]

def get_certainty_equivalent(scoring_array):
    'Used in Player class to evaluate consistency'
    gp = len(scoring_array)
    ce = np.expm1(sum(np.log1p(scoring_array))/gp)
    return ce

def sort_array_descending(array, key):
    if key == 'points_per_gp':
        array.sort(key=lambda x: x.points_per_gp, reverse=True)
    elif key == 'utility':
        array.sort(key=lambda x: x.utility, reverse=True)
    elif key == 'consistency':
        array.sort(key=lambda x: x.consistency, reverse=True)
    elif key == 'points':
        array.sort(key=lambda x: x.points, reverse=True)
    elif key == 'gp':
        array.sort(key=lambda x: x.gp, reverse=True)
    return array

def numpy_rank(array):
    return np.array(array).argsort().argsort()

def get_slot_players(players, slot, method='shuffle'):
    slot_players = [p for p in players if p.slot == slot]
    if method == 'shuffle':
        random.shuffle(slot_players)
    return slot_players

def convert_slot_to_position(slot):
    position = slot[:2]
    tier = int(slot[2:])
    return position, tier 

def convert_position_to_slot(position, tier):
    slot = position + str(tier)
    return slot
