import nltk
import string
import os
import json
import operator
import numpy
from collections import OrderedDict

from sklearn.feature_extraction.text import TfidfVectorizer

path="/Users/.../Crawled_data/data_with_keywords/"
file_list = []
for filename in os.listdir(path):
	if '.json' in filename:
		file_list.append(filename)

print('Total Files: ',len(file_list))
iiTD={}
print("Creating TD Matrix")
for filename in file_list:
	print("File: ",filename)
	json_data = open(path+filename).read()
	Alist = json.loads(json_data)
	City=filename[:-14]
	act_num=0
	for activity in Alist:
		act_num=act_num+1
		ID=City+'*'+str(act_num)
		iiTD[ID]=activity['stemmedKeys']

iiTD_ordered = OrderedDict(sorted(iiTD.items()))

tfidfV = TfidfVectorizer(sublinear_tf=True, stop_words='english')
tfs = tfidfV.fit_transform(iiTD_ordered.values())

allkeys = tfidfV.get_feature_names()

alltfidf=numpy.array([])
for filename in file_list:
	#print("File: ",filename)
	json_data = open(path+filename).read()
	Alist = json.loads(json_data)
	City=filename[:-14]
	act_num=0
	for activity in Alist:
		act_num=act_num+1
		ID=City+'*'+str(act_num)
		keysofAct=activity['stemmedKeys']
		response=tfidfV.transform([keysofAct])
		for col in response.nonzero()[1]:
			alltfidf = numpy.append(alltfidf,response[0, col])

threshold = numpy.percentile(alltfidf, 75, interpolation='higher')

print("Finalising Feature Words for each activity")
for filename in file_list:
	print("File: ",filename)
	json_data = open(path+filename).read()
	Alist = json.loads(json_data)
	City=filename[:-14]
	act_num=0
	kwlist=""
	for activity in Alist:
		act_num=act_num+1
		ID=City+'*'+str(act_num)
		dictionary={}
		keysofAct=activity['stemmedKeys']
		response=tfidfV.transform([keysofAct])
		for col in response.nonzero()[1]:
			dictionary[str(allkeys[col])]=response[0, col]
		sorted_keys = [key for (key,value) in sorted(dictionary.items(),key=operator.itemgetter(1), reverse=True) if value >= threshold]
		if len(sorted_keys)==0:
			continue
		modifiedJ = {"title": activity['title'],"review_url": activity['review_url'],"image_url": activity['image_url'],"category" : activity['category'], "address" : activity['address'], "details" : activity['details'], "all_categories" : activity['all_categories'], "reviews" : activity['reviews'],"features" : sorted_keys}
		modifiedJ = json.dumps(modifiedJ)
		kwlist=kwlist+modifiedJ+','
	kwlist='['+kwlist[:-1]+']'
	outfile = open(path[:-19]+'final_keywords/'+filename[:-14]+"_FinKeys.json",'w')
	outfile.write(kwlist)
	outfile.close()
