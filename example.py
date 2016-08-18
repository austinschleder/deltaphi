from __future__ import print_function
import fantasy_classes as fc
import pandas as pd
import numpy as np

db = 'Drew Brees','qb1',[31.0,35.0,32.0,33.0,34.0]
ar = 'Aaron Rodgers','qb1',[38.0,28.0,21.0,32.0,24.0]
dc = 'Derek Carr','qb1',[28.0,28.0,28.0,28.0,28.0]
af = 'Arian Foster','rb1',[13.0,14.0,15.0,16.0,17.0]
ee = 'Ezekiel Elliot','rb1',[18.0,4.0,12.0,16.0,3.0]
ap = 'Adrian Peterson','rb1',[14.0,14.0,14.0,14.0,14.0]
lm = 'LeSean McCoy','rb2',[12.0,8.0,12.0,10.0,8.0]
dm = 'Doug Martin','rb2',[6.0,9.0,6.0,20.0,9.0]
mi = 'Mark Ingram','rb2',[9.0,9.0,9.0,9.0,9.0]
jj = 'Julio Jones','wr1',[11.0,18.0,5.0,19.0,9.0]
ed = 'Eric Decker','wr1',[10.0,11.0,12.0,13.0,14.0]
ab = 'Antonio Brown','wr1',[11.0,11.0,11.0,11.0,11.0]

sqb1 = 'safe qb1','qb1',[30.0,30.0,30.0]
nqb1 = 'neutral qb1','qb1',[27.0,30.0,33.0]
oqb1 = 'neutral qb1','qb1',[27.0,30.0,33.0]
rqb1 = 'risky qb1','qb1',[20.0,30.0,40.0]
srb1 = 'safe rb1','rb1',[15.0,15.0,15.0]
nrb1 = 'neutral rb1','rb1',[13.0,15.0,17.0]
orb1 = 'neutral rb1','rb1',[13.0,15.0,17.0]
rrb1 = 'risky rb1','rb1',[10.0,15.0,20.0]
srb2 = 'safe qb1','rb2',[10.0,10.0,10.0]
nrb2 = 'neutral rb2','rb2',[8.0,10.0,12.0]
orb2 = 'neutral rb2','rb2',[8.0,10.0,12.0]
rrb2 = 'risky rb2','rb2',[5.0,10.0,15.0]
swr1 = 'safe wr1','wr1',[15.0,15.0,15.0]
nwr1 = 'neutral wr1','wr1',[12.0,15.0,18.0]
owr1 = 'neutral wr1','wr1',[12.0,15.0,18.0]
rwr1 = 'risky wr1','wr1',[2.0,15.0,28.0]
swr2 = 'safe wr2','wr2',[9.0,9.0,9.0]
nwr2 = 'neutral wr2','wr2',[4.0,9.0,14.0]
owr2 = 'neutral wr2','wr2',[4.0,9.0,14.0]
rwr2 = 'risky wr2','wr2',[3.0,4.0,20.0]
ste1 = 'safe te1','te1',[7.0,7.0,7.0]
nte1 = 'neutral te1','te1',[5.0,7.0,9.0]
ote1 = 'neutral te1','te1',[5.0,7.0,9.0]
rte1 = 'risky te1','te1',[3.0,4.0,14.0]

player_data = [
	sqb1, nqb1, oqb1, rqb1, 
	srb1, nrb1, orb1, rrb1, 
	srb2, nrb2, orb2, rrb2, 
	swr1, nwr1, owr1, rwr1, 
	swr2, nwr2, owr2, rwr2, 
	ste1, nte1, ote1, rte1]

players = [fc.Player(x,y,z) for x,y,z in player_data]

roster1 = fc.Roster([players[i] for i in [0,4,8,12,16,20]])
roster2 = fc.Roster([players[j] for j in [1,5,9,13,17,21]])
roster3 = fc.Roster([players[k] for k in [2,6,10,14,18,22]])
roster4 = fc.Roster([players[l] for l in [3,7,11,15,19,23]])

rosters = [roster1, roster2, roster3, roster4]

league1 = fc.League(rosters, ['scoring_goes_here'], len(rosters))

league1.simulate_season(16)

#print(league1.player_names)
#[print(r.player_names, r.scoring_breakdown, r.scoring_output, r.win_expectancies) for r in rosters]
print(league1.points_per_week)
print(league1.win_pct)
print(league1.final_rankings)
[print(r.points_per_week, r.exp_points_per_week) for r in rosters]
