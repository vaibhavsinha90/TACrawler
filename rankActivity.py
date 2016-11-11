import math
import string
import os
import operator, collections
from collections import OrderedDict


def rankActivity(FilteredActivityList, CurrentUV, ClusterInContext, SubclusterDict):
	ClusterOrder=SubclusterDict.get(ClusterInContext)
	#max_index=len(ClusterOrder)-1
	CurrentUV_index=ClusterOrder.index(CurrentUV)
	ActPosDict={}
	for activityID in FilteredActivityList:
		index=ClusterOrder.index(activityID)
		ActPosDict[index]=activityID
	ActPosDict_ordered = OrderedDict(sorted(ActPosDict.items()))
	ActivityList_Ordered=[]
	belowUV={}
	aboveUV={}
	for index,activityID in ActPosDict_ordered.items():
		if index<CurrentUV_index:
			ind=(index - CurrentUV_index)*-1
			belowUV[ind]=activityID
		elif index>CurrentUV_index:
			aboveUV[index - CurrentUV_index]=activityID
		elif index==CurrentUV_index:
			ActivityList_Ordered.append(CurrentUV)
	if len(belowUV)+len(aboveUV)+len(ActivityList_Ordered)!=len(FilteredActivityList):
		print('Wrong! Not all activities split!')
	
	belowUV_List = OrderedDict(sorted(belowUV.items())).values()
	aboveUV_List = OrderedDict(sorted(aboveUV.items())).values()
	common=min(len(belowUV_List),len(aboveUV_List))
	
	## the section below is for debugging only!
	print("below UV length")
	print(len(belowUV))
	print(OrderedDict(sorted(belowUV.items())))
	print(belowUV_List)
	print("above UV length")
	print(len(aboveUV))
	print(OrderedDict(sorted(aboveUV.items())))
	print(aboveUV_List)
	##
	
	for x in range(common):
		ActivityList_Ordered.append(belowUV_List[x])
		ActivityList_Ordered.append(aboveUV_List[x])
	if common==0:
		x=-1
	if len(belowUV_List)!=len(aboveUV_List):
		x=x+1
		if x==len(belowUV_List):
			for i in range(x,len(aboveUV_List)):
				ActivityList_Ordered.append(aboveUV_List[i])
		elif x==len(aboveUV_List):
			for i in range(x,len(belowUV_List)):
				ActivityList_Ordered.append(belowUV_List[i])
		else:
			print('Wrong! sth went wrong with indexing!')
	if len(ActivityList_Ordered)!=len(FilteredActivityList):
		print('Wrong! Not all activities ordered!')
	return ActivityList_Ordered
