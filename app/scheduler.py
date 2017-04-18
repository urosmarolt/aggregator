from eventregistry import *
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient

#client = MongoClient('localhost', 27017)
client = MongoClient("mongodb://127.0.0.1:27017")
db = client.newsItems


def pullItems():
    query = db.config.find().limit(1)
    er = EventRegistry()
    #er.login(query[0]['loginUser'], query[0]['loginPass'])


    q = QueryArticles()
    q.addCategory("dmoz/" + query[0]['aggregatorCategory'])
    q.addKeyword(query[0]['aggregatorKeyword'])
    q.addConcept(er.getConceptUri(query[0]['aggregatorTheme']))
    # return details about the articles
    q.addRequestedResult(RequestArticlesInfo(count=50,returnInfo=ReturnInfo(articleInfo=ArticleInfoFlags(duplicateList=True, concepts=False,categories=False, location=False,image=True))))
    # execute the query
    res = er.execQuery(q)

    for item in res['articles']['results']:
        print(item)
        try:
            #cleanup dict raw data structure
            del item["sim"]
            del item["duplicateList"]
            del item["wgt"]
            del item["eventUri"]
            del item["uri"]

            item["sourceUrl"] = item["source"]["uri"]
            item["sourceTitle"] = item["source"]["title"]
            del item["source"]
            item["datetime"] = item["date"] + " " + item["time"]
            del item["date"]
            del item["time"]
            item["sourceID"] = item["id"]
            del item["id"]
            print(item["isDuplicate"])
            if item["isDuplicate"] == False:
                del item["isDuplicate"]
                saveToDB(item)
        except Exception as e:
            print("Error \n %s" % (e))



def saveToDB(item):
    db.post.insert(item)



pullItems()
#sched = BackgroundScheduler()
#sched.add_job(pullItems, trigger='cron', hour='6')
#sched.start()
