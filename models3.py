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

	def __init__(self):
		print('League created!')

class Player_DB:
	"""
	Holds every Player object.
	In addition to creating Players from game logs, it should have functions for
	sorting, filtering, and returning Players based on different attributes.
	"""

	def __init__(self):
		print('Player_DB created!')

class Player:
	"""
	Contains name, position, and scoring_array for a particular player.
	Persists throughout league, reassigned to new roster/team every season.
	Should it contain slot/tier information (AKA 'rb' versus 'rb1')?
	Should it store results (Player.scoring_output[season][week]) or does that go somewhere else?
	"""

	def __init__(self):
		print('Player created!')

class Team:
	"""
	Contains team nickname.
	Persists throughout league, reassigned new roster/players every season.
	Should it store results (Player.scoring_output[season][week]) or does that go somewhere else?
	"""

	def __init__(self):
		print('Team created!')

class Season:
	"""
	Contains final standings and team rank.
	"""

	def __init__(self):
		print('Season created!')





