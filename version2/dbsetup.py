from models import *
import pickle

with open('snippet.pickle', 'rb') as fr:
	qsl = pickle.load(fr)

Algorithm(name='0g').save()
Algorithm(name='01gfp').save()
Algorithm(name='05gfp').save()
Algorithm(name='09gfp').save()

qid = 1
for q in qsl:
	Query(query_name=q.query, query_id=qid).save()
	qid += 1
