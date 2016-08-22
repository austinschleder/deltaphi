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
        self.league_size = len(teams)

        self.set_rosters()
        self.generate_player_scores()
        self.calculate_team_scores()
        self.calculate_weekly_stats()
        self.calculate_season_stats()
        self.calculate_player_value()

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

    def get_slot_players(self, slot):
        slot_players = [p for p in self.players if p.slot == slot]
        return slot_players

    # def set_rosters(self):
    #     'Set rosters according to slot (i.e., only the 11-20th best wrs go in a wr2 slot)'
    #     seasons = self.seasons
    #     teams = self.teams
    #     players = self.players
    #     roster_slots = self.roster_slots
    #     for s in seasons:
    #         rosters = {t.team_id: [] for t in teams}
    #         num_teams = len(teams)
    #         for slot in roster_slots:
    #             slot_players = get_slot_players(players, slot)
    #             assignments = zip(teams, slot_players)
    #             [rosters[t.team_id].append(p.player_id) for t, p in assignments]
    #             [p.update_team_assignment(s.season_id, t.team_id) for t, p in assignments]
    #         s.rosters = rosters
    #         [t.update_player_assignments(s.season_id, rosters[t.team_id]) for t in teams]

    def set_rosters(self):
        'Set rosters without regard to slots (i.e., wr1 can go in a wr2 slot)'
        seasons = self.seasons
        teams = self.teams
        players = self.players
        roster_positions = ['qb', 'rb', 'wr', 'te']
        roster_openings = {'qb':1, 'rb':2, 'wr':3, 'te':1}
        for pos in roster_positions:
            position_players = get_position_players(players, pos)
            calculate_position_measurements(position_players)
        for s in seasons:
            rosters = {t.team_id: [] for t in teams}
            for pos in roster_positions:
                position_players = get_position_players(players, pos)
                team_ids = np.repeat([t.team_id for t in teams], roster_openings[pos])
                assignments = zip(team_ids, position_players)
                [rosters[tid].append(p.player_id) for tid, p in assignments]
                [p.update_team_assignment(s.season_id, tid) for tid, p in assignments]
            s.rosters = rosters
            [t.update_player_assignments(s.season_id, rosters[t.team_id]) for t in teams]


    def generate_player_scores(self):
        seasons = self.seasons
        players = self.players
        for s in seasons:
            season_length = s.season_length
            for p in players:
                #p.update_scoring_output(s.season_id, [random.choice(p.scoring_array) for i in xrange(season_length)])
                p.update_scoring_output(s.season_id, [p.scoring_array[i] for i in xrange(season_length)])

    def calculate_team_scores(self):
        seasons = self.seasons
        teams = self.teams
        players = self.players
        for s in seasons:
            season_length = s.season_length
            for t in teams:
                weekly_output = [sum(p.scoring_output[s.season_id][i] for p in players if p.team_assignments[s.season_id] == t.team_id) for i in xrange(season_length)]
                t.update_scoring_output(s.season_id, weekly_output)

    def calculate_weekly_stats(self):
        seasons = self.seasons
        teams = self.teams
        for s in seasons:
            season_length = s.season_length
            league_size = len(teams)
            matchup_rankings_by_week = [numpy_rank([t.scoring_output[s.season_id][i] for t in teams]) for i in xrange(season_length)]
            matchup_rankings_by_team = map(list, zip(*matchup_rankings_by_week))
            [s.update_team_rankings_weekly(teams[i].team_id, matchup_rankings_by_team[i]) for i in xrange(league_size)]

    def calculate_season_stats(self):
        seasons = self.seasons
        teams = self.teams
        players = self.players
        league_size = self.league_size
        for s in seasons:
            season_length = s.season_length
            [s.update_team_win_pct(t.team_id, float(sum(s.team_rankings[t.team_id]))/((league_size-1)*season_length)) for t in teams]
            team_ids = [t.team_id for t in teams]
            final_team_ranks = numpy_rank([s.team_win_pct[t.team_id] for t in teams])
            [s.update_final_team_ranks(team_id, rank) for team_id, rank in zip(team_ids, final_team_ranks)]
            [p.update_team_rankings(s.season_id, s.final_team_ranks[p.team_assignments[s.season_id]]) for p in players]

    def calculate_player_value(self):
        players = self.players
        league_size = len(self.teams)
        [p.update_average_team_ranking(10-sum(p.team_rankings.values())/float(len(p.team_rankings))) for p in players]
        [p.update_harmonic_team_ranking(len(p.team_rankings)/sum([1.0/(10-r) for r in p.team_rankings.values()])) for p in players]
        [p.update_champion_pct(sum([1 for tr in p.team_rankings.values() if tr == (league_size-1)])/float(len(p.team_rankings))) for p in players]

class Player_DB:
    """
    Holds every Player object.
    In addition to creating Players from game logs, it should have functions for
    sorting, filtering, and returning Players based on different attributes.
    """
    id = 1

    def __init__(self, game_logs, scoring_categories, scoring_values, season_length, injury_handling):
        self.db_id = 'DB' + str(Player_DB.id)
        Player_DB.id += 1
        pdb = analyze_game_logs(game_logs, scoring_categories, scoring_values)
        self.players = create_players_from_pdb(pdb, season_length, injury_handling)
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

    def __init__(self, name, position, scoring_array, injury_handling, season_length):
        self.player_id = 'P' + str(Player.id).zfill(3)
        Player.id += 1
        self.name = name
        self.position = position
        self.historic_scoring_array = scoring_array
        self.points = sum(scoring_array)
        self.gp = len(scoring_array)
        self.scoring_array = generate_scoring_array(scoring_array, injury_handling, season_length)
        self.points_per_gp = sum(self.scoring_array)/len(self.scoring_array)
        self.utility = get_certainty_equivalent(self.scoring_array)
        self.consistency = self.utility/self.points_per_gp
        self.median_score = np.median(scoring_array)
        self.slot = position
        self.position_averages = {}
        self.position_rank = 0
        self.team_assignments = {}
        self.scoring_output = {}
        self.average_points = {}
        self.average_utility = {}
        self.season_consistency = {}
        self.team_rankings = {}
        self.average_team_ranking = []
        self.harmonic_team_ranking = []
        self.champion_pct = []

    def __str__(self):
        return '{} {}: {:20s} ({}) -- Avg: {:5.2f} | Hrm: {:5.2f} | Champ: {:5.2f} | P: {:5.2f} | U: {:5.2f} | C: {:5.2f}'.format(self.__class__.__name__, self.player_id, self.name, self.slot, 5 - self.average_team_ranking[0], 3.414 - self.harmonic_team_ranking[0] , self.champion_pct[0] - 0.1, self.points_per_gp_normalized, self.utility_normalized, self.consistency)

    def set_slot(self, slot):
        self.slot = slot

    def set_position_rank(self, position_rank):
        self.position_rank = position_rank

    def update_position_averages(self, measurement_dict):
        self.position_averages.update(measurement_dict)
        self.points_per_gp_normalized = (self.points_per_gp - measurement_dict['avg_points_per_gp'])/measurement_dict['std_points_per_gp']
        self.points_per_gp_excess = self.points_per_gp - measurement_dict['min_points_per_gp']
        self.utility_normalized = (self.utility - measurement_dict['avg_utility'])/measurement_dict['std_utility']
        self.utility_excess = self.utility - measurement_dict['min_utility']
        self.consistency_normalized = (self.consistency - measurement_dict['avg_consistency'])/measurement_dict['std_consistency']
        self.consistency_excess = self.consistency - measurement_dict['min_consistency']

    def update_team_assignment(self, season_id, team_id):
        self.team_assignments.update({season_id: team_id})

    def update_scoring_output(self, season_id, seasonal_scoring):
        average_points = sum(seasonal_scoring)/len(seasonal_scoring)
        average_utility = get_certainty_equivalent(seasonal_scoring)
        self.scoring_output.update({season_id: seasonal_scoring})
        self.average_points.update({season_id: average_points})
        self.average_utility.update({season_id: average_utility})
        self.season_consistency.update({season_id: average_utility/average_points})

    def update_team_rankings(self, season_id, team_rank):
        self.team_rankings.update({season_id: team_rank})

    def update_average_team_ranking(self, average_rank):
        self.average_team_ranking.append(average_rank)

    def update_harmonic_team_ranking(self, harmonic_rank):
        self.harmonic_team_ranking.append(harmonic_rank)

    def update_champion_pct(self, champion_pct):
        self.champion_pct.append(champion_pct)

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
        self.average_points = {}
        self.average_utility = {}
        self.weekly_consistency = {}

    def __str__(self):
        return '{} {}: {} -- {} '.format(self.__class__.__name__, self.team_id, self.nickname, self.player_assignments)

    def update_player_assignments(self, season_id, roster):
        self.player_assignments.update({season_id: roster})

    def update_scoring_output(self, season_id, seasonal_scoring):
        average_points = sum(seasonal_scoring)/len(seasonal_scoring)
        average_utility = get_certainty_equivalent(seasonal_scoring)
        self.scoring_output.update({season_id: seasonal_scoring})
        self.average_points.update({season_id: average_points})
        self.average_utility.update({season_id: average_utility})
        self.weekly_consistency.update({season_id: average_utility/average_points})

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
        self.final_team_ranks = {}
        self.team_win_pct = {}

    def __str__(self):
        return '{} {}: {} / {}'.format(self.__class__.__name__, self.season_id, self.team_win_pct, self.final_team_ranks)

    def generate_player_scores(self, players):
        season_length = self.season_length
        season_id = self.season_id
        [p.update_scoring_output(season_id, [random.choice(p.scoring_array) for i in xrange(season_length)]) for p in players]

    def update_team_rankings_weekly(self, team_id, matchup_rankings_by_team):
        self.team_rankings.update({team_id: matchup_rankings_by_team})

    def update_team_win_pct(self, team_id, win_pct):
        self.team_win_pct.update({team_id: win_pct})

    def update_final_team_ranks(self, team_id, rank):
        self.final_team_ranks.update({team_id: rank})

###############
## Functions ##
###############

def analyze_game_logs(game_logs, scoring_categories, scoring_values):
    game_logs['points'] = game_logs[scoring_categories].dot(scoring_values)
    gl = game_logs[['player', 'position', 'points']]
    pdb = gl.groupby(['player', 'position'], as_index=False)['points'].apply(list).reset_index(name='scoring_array')
    return pdb

def create_players_from_pdb(pdb, season_length, injury_handling):
    players = [Player(pdb['player'][p], pdb['position'][p], pdb['scoring_array'][p], season_length, injury_handling) for p in xrange(len(pdb))]
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

def generate_scoring_array(scoring_array, season_length, injury_handling='zeros'):
    gp = len(scoring_array)
    games_missed = season_length - gp
    score_avg = np.average(scoring_array)
    score_std = np.std(scoring_array)+.01
    if games_missed:
        if injury_handling == 'zeros':
            [scoring_array.append(0) for i in xrange(games_missed)]
        elif injury_handling == 'recycle':
            [scoring_array.append(random.choice(scoring_array)) for i in xrange(games_missed)]
        elif injury_handling == 'impute':
            [scoring_array.append(np.absolute(np.random.normal(score_avg, score_std))) for i in xrange(games_missed)]
        elif injury_handling == 'normal':
            scoring_array = [np.absolute(np.random.normal(score_avg, score_std)) for i in xrange(season_length)]
        else:
            print('Options for handling injuries include "zeros", "recycle", or "impute".')
    random.shuffle(scoring_array)
    return scoring_array

def get_certainty_equivalent(scoring_array):
    'Used in Player class to evaluate consistency'
    gp = len(scoring_array)
    ce = np.expm1(sum(np.log1p(scoring_array))/gp)
    #ce = np.expm1(np.expm1(sum(np.log1p(np.log1p(scoring_array)))/gp))
    #ce = np.expm1(np.expm1(np.expm1(sum(np.log1p(np.log1p(np.log1p(scoring_array))))/gp)))
    #ce = np.square(sum(np.sqrt(np.absolute(scoring_array)))/gp)
    #ce = np.expm1(np.sqrt(sum(np.square(np.log1p(scoring_array)))/gp))
    #ce = np.log1p(sum(np.expm1(scoring_array))/gp)
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

def calculate_position_measurements(position_players):
    min_points_per_gp = min([p.points_per_gp for p in position_players])
    avg_points_per_gp = np.average([p.points_per_gp for p in position_players])
    std_points_per_gp = np.std([p.points_per_gp for p in position_players])
    min_utility = min([p.utility for p in position_players])
    avg_utility = np.average([p.utility for p in position_players])
    std_utility = np.std([p.utility for p in position_players])
    min_consistency = min([p.consistency for p in position_players])
    avg_consistency = np.average([p.consistency for p in position_players])
    std_consistency = np.std([p.consistency for p in position_players])
    measurements = [min_points_per_gp, avg_points_per_gp, std_points_per_gp, min_utility, avg_utility, std_utility, min_consistency, avg_consistency, std_consistency]
    measurement_names = ['min_points_per_gp', 'avg_points_per_gp', 'std_points_per_gp', 'min_utility', 'avg_utility', 'std_utility', 'min_consistency', 'avg_consistency', 'std_consistency']
    measurement_dict = {z[0]: z[1] for z in zip(measurement_names, measurements)}
    [p.update_position_averages(measurement_dict) for p in position_players]

def get_slot_players(players, slot, method='shuffle'):
    slot_players = [p for p in players if p.slot == slot]
    if method == 'shuffle':
        random.shuffle(slot_players)
    return slot_players

def get_position_players(players, position, method='shuffle'):
    position_players = [p for p in players if p.position == position]
    if method == 'shuffle':
        random.shuffle(position_players)
    return position_players

def convert_slot_to_position(slot):
    position = slot[:2]
    tier = int(slot[2:])
    return position, tier 

def convert_position_to_slot(position, tier):
    slot = position + str(tier)
    return slot
