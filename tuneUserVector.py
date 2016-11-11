import numpy as np
np.set_printoptions(precision=5, suppress=True)
import math, string, os, random, operator, collections, sys
from collections import OrderedDict
sys.setrecursionlimit(10000)

def FloatScoreToInt(score):
	max_score = 1.0
	intervalLength=round(1/max_score,2)
	#print(intervalLength)
	separators=[0.00]
	ub=intervalLength
	while ub!=1:
		separators.append(ub)
		#print(separators)
		ub=round(ub+intervalLength,2)
		#print(ub)
	separators.append(1.00)
	if int(score)==1:
		return max_score
	decided_score=0
	temp_score=0
	for s in range(len(separators)):
		temp_score+=1
		if score>=separators[s] and score<separators[s+1]:
			decided_score=temp_score
	if decided_score==0:
		print('Something went wrong while converting the score')
		return 1
	return decided_score

# 0.0 - 1.0
# 0.0 - 0.5 > negative score | 0.5 - 1.0 > positive
# reviewType > subjective | objective
# reviewedActivityRank  rank in listed activities
def tuneUserVector(ReviewScore, ReviewType, clusterInContextDict, ReviewedActivityRank, ReviewedActivityID, CurrentUV):
	print("**** TUNING USER VECTOR ****")
	print("\nreview type")
	print(ReviewType)
	print("\nReviewedActivityRank")
	print(ReviewedActivityRank)
	print("\nReviewedActivityID")
	print(ReviewedActivityID)
	print("\nCurrentUV")
	print(CurrentUV)
	print("\n")
	max_score = 5
	if ReviewType=='subjective':
		if ReviewScore == 0:
			ReviewScore = 1
		elif ReviewScore == 1:
			ReviewScore = 5
	ScoreCombo=str(ReviewedActivityRank)+'->'+str(ReviewScore)
	print("score combo " + ScoreCombo)
	print("\nreview score")
	print(ReviewScore)
	
	#building MovementLength Map(some lists) based on (Rabk->Score) combos and deciding MovementLength
	Move1=['1->5','2->4','4->2','5->1']
	Move2=['1->x','2->x','3->x','4->x','5->x']
	Move3=['1->1','2->2','4->4','5->5']
	MovementLength=0
	num=len(clusterInContextDict)   #NumberofActivitiesinCluster
	m1=math.ceil(num*0.05)
	m2=math.ceil(num*0.10)
	m3=math.ceil(num*0.15)
	if m1==0 or m2==0 or m3==0:
		m1=1
		m2=2
		m3=3
	if ScoreCombo in Move1:
		MovementLength=m1
		print("moving length 1")
	elif ScoreCombo in Move3:
		MovementLength=m3
		print("moving length 3")
	elif ScoreCombo=='3->3':
		MovementLength=random.choice([m1,m3])
		print("moving length random")

	if MovementLength==0:
		ScoreCombo=ScoreCombo[:-1]+'x'
	if ScoreCombo in Move2:
		MovementLength=m2

	#Finding if the ReviewedActivity is below or above the CurrentUV activity in the clusterInContextDict 
	UV_index=clusterInContextDict.index(CurrentUV)
	Activity_index=clusterInContextDict.index(ReviewedActivityID)
	is_below_UV='no'
	if Activity_index<=UV_index:
		is_below_UV='yes'

	#Deciding MovementDirection (0->DownTheOrder(towards the centroid i.e. 0th index); 1->UpTheOrder)
	MovementDirection = -1
	mid_score = math.ceil(max_score/2)
	if ReviewScore==mid_score:
		MovementDirection=random.randrange(0,2)
	elif ReviewScore<mid_score:
		if is_below_UV=='yes':
			MovementDirection=1
		else:
			MovementDirection=0
	elif ReviewScore>mid_score:
		if is_below_UV=='yes':
			MovementDirection=0
		else:
			MovementDirection=1

	if MovementDirection < 0:
		print("Something went wrong with direction calculation1!")

	#Calculate New UserVector
	NewUV_index = None
	NewUV=''
	if MovementDirection==0:
		NewUV_index = UV_index - MovementLength
	elif MovementDirection==1:
		NewUV_index = UV_index + MovementLength

	if NewUV_index == None:
		print("Something went wrong with direction calculation2!")
		return CurrentUV

	if NewUV_index<0:
		NewUV_index=0
		print('Warning! Reached 0!')
	if NewUV_index>(len(clusterInContextDict)-1):
		NewUV_index=len(clusterInContextDict)-1
		print('Warning! Reached Max index!')
	NewUV=clusterInContextDict[NewUV_index]
	return NewUV
