from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy import linalg
import numpy as np
np.set_printoptions(precision=5, suppress=True)
import nltk
import string
import os
import json
import operator, collections
import numpy
from collections import OrderedDict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.random_projection import sparse_random_matrix

from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist, squareform

import sys
sys.setrecursionlimit(10000)

def PlotClusterCategories(ClusterCategCounter):
	labels, values = zip(*ClusterCategCounter.items())
	indexes = np.arange(len(labels))
	width = 1
	plt.figure(figsize=(25, 8))
	plt.bar(indexes, values, width)
	plt.xticks(indexes + width * 0.5, labels,rotation=90)
	plt.show()
	return

def PlotDendogram(HierarchyOrder,i=None):
	plt.figure(figsize=(25, 10))
	if i==None:
		plt.title('Clustering Dendrogram')
	else:
		plt.title('Clustering'+str(i)+' Dendrogram')
	plt.xlabel('ID_space')
	plt.ylabel('Distance')
	dendrogram(
	    HierarchyOrder,
	    #truncate_mode='lastp',
	    #p=20,
	    #show_leaf_counts=False,
	    leaf_rotation=90.,
	    leaf_font_size=10.,
	    #show_contracted=True,
	)
	plt.show()
	#plt.close()
	return


global uniquekeys
path="/Users/.../Crawled_data/final_keywords/"
file_list = []
for filename in os.listdir(path):
	if '.json' in filename:
		file_list.append(filename)

act_num=0
act_num_in_city=0
print('Total Files: ',len(file_list))

iiTD={}
ActData={}
uniquekeys=set([])
uniqueCateg=set([])
titles=[]
uk=[]
uk4med=[]
max_ukinact=0
totuk=0
min_ukinact=2898370
#file_listtemp=['g60814_Finkeys.json']
for filename in file_list:
	print("File: ",filename)
	json_data = open(path+filename).read()
	Alist = json.loads(json_data)
	City=filename[:-13]
	act_num_in_city=0
	for activity in Alist:
		act_num_in_city=act_num_in_city+1
		act_num=act_num+1
		ID=City+'*'+str(act_num_in_city)
		iiTD[ID]=' '.join(activity['features'])
		uniquekeys.update(activity['features'])
		ukinact=set(activity['features'])
		totuk=totuk+len(ukinact)
		uk4med.append(len(ukinact))
		if len(ukinact)>max_ukinact:
			max_ukinact=len(ukinact)
		if len(ukinact)<min_ukinact:
			min_ukinact=len(ukinact)
		uk.extend(activity['features'])
		titles.append(activity['title'])
		act_categ=activity['all_categories']+[activity['category']]
		uniqueCateg.update(act_categ)
		ActData[ID]=(activity['title'],act_categ,activity['features'])
	#print(act_num_in_city)

print('# of Uniquekeys:',len(uniquekeys))
print('# of Activities:',act_num)
print('# of Activities by title:',len(titles))
print('# of uk:',len(uk))

print('Max uk in an activity:',max_ukinact)
print('Min uk in an activity:',min_ukinact)
print('Avg uk in an activity:',totuk/act_num)
MedianUniqueKeys=numpy.percentile(uk4med, 50, interpolation='higher')
print('Median uk in an activity:',MedianUniqueKeys)



#----assigning index value to all unique terms
featureIndex={}  #vocab_dict
position=0
for feature in uniquekeys:
    featureIndex[feature]=position
    position+=1

#---creating tf-idf weighted TD Matrix for LSA
#CAN ALSO TRY: just tf or log-entropy i.e.take the log of each frequency, and multiply the whole term vector by the entropy of the vector.
iiTD_ordered = OrderedDict(sorted(iiTD.items()))
tfidfV = TfidfVectorizer(stop_words='english',vocabulary=featureIndex,sublinear_tf=True)
tfs = tfidfV.fit_transform(iiTD_ordered.values())  #---(doc#,feature#)
print('TD matrix dimensions :', tfs.shape)

#---SVD!
svd = TruncatedSVD(n_components=MedianUniqueKeys,algorithm="arpack")   #CAN ALSO TRY: some% of #of Features instead of fixed n_components OR change algo arpack/randomized
svd.fit(tfs)
Sigma=svd.transform(tfs)
print('Reduced Dimensions of TD Matrix', Sigma.shape)



#---clustering!
Clustering_Order = linkage(Sigma,method='ward', metric='euclidean')  #can also provide a consistency constraint by making a graph of activities linked by category values. See http://scikit-learn.org/stable/tutorial/statistical_inference/unsupervised_learning.html
c, coph_dists = cophenet(Clustering_Order, pdist(Sigma))
print(str(c))
#print(Clustering_Order)
plt.figure(figsize=(25, 10))
plt.title('Clustering Dendrogram')
plt.xlabel('ID_space')
plt.ylabel('Distance')
dendrogram(
    Clustering_Order,
    #truncate_mode='lastp',
    #p=20,
    #show_leaf_counts=False,
    leaf_rotation=90.,
    leaf_font_size=10.,
    #show_contracted=True,
)
plt.show()


#----------Extracting Flat Clusters and confirming they are correct
num_of_clusters=5
k=list(iiTD_ordered.keys())
#v=list(iiTD_ordered.values())
#print(k[1])
#print(v[1])
#print(ActData[k[1]][1])
FinClusters=fcluster(Clustering_Order, num_of_clusters, criterion = "maxclust")
print('Flat Clusters matrix\'s dimensions :', FinClusters.shape)

#---build an ID:clusterNumber dict
ClusterDict={}
actNum=0
for act in k:
	ClusterDict[act]=FinClusters[actNum]
	actNum=actNum+1

#---build an ID:ActivityVector dict
VectorDict={}
actNum=0
for act in k:
	VectorDict[act]=list(Sigma[actNum,:])
	actNum=actNum+1

#---Data Analysis (Important to identify topic of the cluster)
print('# of Unique Categories:',len(uniqueCateg))
ClusterCounter = collections.Counter(FinClusters)
print('# of activities in each cluster:', ClusterCounter)

Cluster1 = collections.Counter()
Cluster2 = collections.Counter()
Cluster3 = collections.Counter()
Cluster4 = collections.Counter()
Cluster5 = collections.Counter()
actNum=0
for act in k:
	assignedCluster=FinClusters[actNum]
	Categories=ActData.get(act)[1]
	actNum=actNum+1
	if assignedCluster==1:
		Cluster1.update(Categories)
	elif assignedCluster==2:
		Cluster2.update(Categories)
	elif assignedCluster==3:
		Cluster3.update(Categories)
	elif assignedCluster==4:
		Cluster4.update(Categories)
	else:
		Cluster5.update(Categories)
print('Following is the number of unique categories in each cluster:')
print('1: ',len(Cluster1))
print('2: ',len(Cluster2))
print('3: ',len(Cluster3))
print('4: ',len(Cluster4))
print('5: ',len(Cluster5))



#Re-cluster each flatCluster
VecDic_ordered=OrderedDict(sorted(VectorDict.items()))
ClustDic_ordered=OrderedDict(sorted(ClusterDict.items()))
SubClusterOrders={}
for i in range(1,num_of_clusters+1):
	SubClusterMatrix=np.empty([ClusterCounter.get(i),Sigma.shape[1]])
	ActivityPositionalIndex={}
	actCount=0
	for ID,Cnum in ClustDic_ordered.items():
		if Cnum==i:
			ActivityPositionalIndex[actCount]=ID
			SubClusterMatrix[actCount,:]=VecDic_ordered.get(ID)
			actCount+=1
	print('Shape of subcluster Matrix of Cluster#',str(i),SubClusterMatrix.shape)
	SubClustering_Order = linkage(SubClusterMatrix,method='ward', metric='euclidean')
	#print(type(SubClustering_Order))
	print(SubClustering_Order.shape)
	NumActivities=SubClustering_Order.shape[0]
	OrderOfMerge=[]
	for n in range(NumActivities):
		index=SubClustering_Order[n,:][0]
		if(index<NumActivities):
			OrderOfMerge.append(ActivityPositionalIndex.get(index))
		index=SubClustering_Order[n,:][1]
		if(index<NumActivities):
			OrderOfMerge.append(ActivityPositionalIndex.get(index))
	print('Order of Merging (length):',len(OrderOfMerge))
	SubClusterOrders[i]=OrderOfMerge



#------Save SubClustering Orders to file
outfile = open(path[:-15]+'processed_data/'+"SubClusterOrders.txt",'w')
for clustNum in range(1,num_of_clusters+1):
	order=SubClusterOrders.get(clustNum)
	print('Medoid for Cluster',str(clustNum),': ',order[0], ' ~~~~ Title: ',ActData.get(order[0])[0])
	outfile.write(str(clustNum)+':'+str(order)+'\n')
outfile.close()

#----Inserting clustering Detail into Data
print('Inserting clustering Detail into Data...')
for filename in file_list:
	print("Reading File: ",filename)
	json_data = open(path+filename).read()
	Alist = json.loads(json_data)
	City=filename[:-13]
	act_num_in_city=0
	kwlist=""
	for activity in Alist:
		act_num_in_city=act_num_in_city+1
		ID=City+'*'+str(act_num_in_city)
		act_categ=activity['all_categories']+[activity['category']]
		ActivityVecAsCSV=""
		for val in VectorDict.get(ID):
			ActivityVecAsCSV=ActivityVecAsCSV+str(val)+','
		modifiedJ = {"activityID":ID, "activity_vector":ActivityVecAsCSV[:-1] , "cluster_num": str(ClusterDict.get(ID)) , "title": activity['title'],"review_url": activity['review_url'],"image_url": activity['image_url'],"category" : activity['category'], "address" : activity['address'], "details" : activity['details'], "all_categories" : act_categ, "reviews" : activity['reviews'],"features" : activity['features']}
		modifiedJ = json.dumps(modifiedJ)
		kwlist=kwlist+modifiedJ+','
	kwlist='['+kwlist[:-1]+']'
	outfile = open(path[:-15]+'processed_data/'+filename[:-13]+"_Clustered.json",'w')
	outfile.write(kwlist)
	outfile.close()
