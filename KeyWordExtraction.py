import textacy
import json
import math
import os
from unidecode import unidecode
import re, collections
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import nltk
import string
import operator
import numpy

from sklearn.feature_extraction.text import TfidfVectorizer

def makeCorpus(review):
	global ReviewCorpus
	global idfDict
	global rc
	
	l=textacy.text_utils.detect_language(review)
	if l!='en':
		print('review not added')
		return
	review=textacy.preprocess.normalize_whitespace(unidecode(review))
	review=textacy.preprocess.preprocess_text(review, no_contractions=True)
	review=textacy.preprocess.replace_urls(review, replace_with='')
	review=textacy.preprocess.replace_emails(review, replace_with='')
	'''
	review_doc = textacy.texts.TextDoc(review.strip(), lang='en')
	ReviewCorpus.add_doc(review_doc, print_warning=True)
	'''
	
	review_doc = textacy.texts.TextDoc(review.strip(), lang='en')
	review_span = review_doc[0 : len(review_doc)+1]
	RevText_norm = textacy.spacy_utils.normalized_str(review_span)
	#print(RevText_norm)
	review_doc = textacy.texts.TextDoc(RevText_norm.strip(), lang='en')	
	ReviewCorpus.add_doc(review_doc, print_warning=True)
	

	doc_unique_words=set(review_doc.term_counts(lemmatize='auto', ngram_range=(1, 1)))
	counterforidf = collections.Counter()
	counterforidf.update(doc_unique_words)
	idfDict=idfDict+counterforidf
	rc=rc+1
	return


global ReviewCorpus
global idfDict
global rc
path="/Users/.../Crawled_data/"
file_list = []
for filename in os.listdir(path+'data/'):
	if '.json' in filename:
		file_list.append(filename)
print(str(len(file_list))+' number of cities...')

CityCodes={}
with open(path+'CityList1_orig.txt') as fileContents:
    for line in fileContents:
        citydata=line.split(';')
        CityCodes.update({citydata[1][:-6]: citydata[0]})
#print(CityCodes)

for filename in file_list:
	print("File: ",filename)
	json_data = open(path+'data/'+filename).read()
	Alist = json.loads(json_data)
	act=0
	kwlist=""
	for activity in Alist:
		rc=0
		ReviewCorpus=textacy.texts.TextCorpus('en')
		idfDict=collections.Counter()
		act=act+1
		print("Activity:",act)
		Rlist=activity['reviews']
		if len(Rlist)==0:
			act=act-1
			continue
		for review in Rlist:
			makeCorpus(review)
		num_of_docs=rc
		idf=collections.Counter({term : math.log2(num_of_docs/idfDict[term]) for term in idfDict.keys()})
		idfDict=collections.Counter()    #---freeing some memory
		Kir=[]
		for review_doc in ReviewCorpus:
			#KeywordsInReview=textacy.keyterms.sgrank(review_doc, window_width=1500, idf=idf)
			#Kir.extend(kw_tuple[0] for kw_tuple in KeywordsInReview)
			Kir.extend(textacy.keyterms.sgrank(review_doc, window_width=1500, idf=idf))   #could be some % of num of tokens in review_doc instead of 1500
		Kir.sort(key=operator.itemgetter(1), reverse=True)
		print(Kir)
		Kir2=[]
		Kir2.extend(kw_tuple[0] for kw_tuple in Kir)
		modifiedJ = {"title": activity['title'],"review_url": activity['review_url'],"image_url": activity['image_url'],"category" : activity['category'], "details" : activity['details'], "all_categories" : activity['all_categories'], "reviews" : activity['reviews'], "keywords" : Kir2}
		modifiedJ = json.dumps(modifiedJ)
		kwlist=kwlist+modifiedJ+','
		del Kir[:]
	kwlist='['+kwlist[:-1]+']'

	#-----------Now split the identified keywords

	StopWords = stopwords.words("english")
	json_data = kwlist
	Alist = json.loads(json_data)
	kwlist=""
	for activity in Alist:
		Klist=activity['keywords']
		splitKeys=[]
		OneBlockKeys=""
		for keywrd in Klist:
			sk=re.split(r'[,;/ ]+',keywrd)
			for k in sk:
				splitKeys.append(k)
		OneBlockKeys = ' '.join([word for word in splitKeys if (word not in StopWords and '.' not in word)])
		modifiedJ = {"title": activity['title'],"review_url": activity['review_url'],"image_url": activity['image_url'],"category" : activity['category'], "details" : activity['details'], "all_categories" : activity['all_categories'], "reviews" : activity['reviews'], "splitKeys" : OneBlockKeys}
		modifiedJ = json.dumps(modifiedJ)
		kwlist=kwlist+modifiedJ+','
	kwlist='['+kwlist[:-1]+']'

	#-----------Now stemming the unigram keywords
'''
	stemmer = PorterStemmer()
	json_data = kwlist
	Alist = json.loads(json_data)
	kwlist=""
	for activity in Alist:
		OneBlock=activity['splitKeys']
		stemmedKeys=[]
		One_sk=""
		unstemmedKeys=OneBlock.split(" ")
		for usk in unstemmedKeys:
			usklist= usk.lower()
			stemmedKL=stemmer.stem(usklist)
			stemmedKeys.append(stemmedKL)
		One_sk = ' '.join([word for word in stemmedKeys])
		
		adrs=[]
		if 'streetAdd' in activity['details']:
			if activity['details']['streetAdd'].strip()!='':
				adrs.append(activity['details']['streetAdd'].strip())
		if 'loc_name' in activity['details']:
			if activity['details']['loc_name'].strip()!='':
				adrs.append(activity['details']['loc_name'].strip())
		if 'locality' in activity['details']:
			if activity['details']['locality'].strip()!='':
				adrs.append(activity['details']['locality'].strip())
		adrs_str =''
		if len(adrs)!=0:
			adrs_str=', '.join(adrs)
		modifiedJ = {"title": activity['title'],"review_url": activity['review_url'],"image_url": activity['image_url'],"category" : activity['category'],"address": adrs_str, "details" : activity['details'], "all_categories" : activity['all_categories'], "reviews" : activity['reviews'],"stemmedKeys" : One_sk}
		modifiedJ = json.dumps(modifiedJ)
		kwlist=kwlist+modifiedJ+','
	kwlist='['+kwlist[:-1]+']'
	outfile = open(path+'data_with_keywords/'+CityCodes[filename[:-16]]+"_KeyWords.json",'w')
	outfile.write(kwlist)
	outfile.close()
'''
