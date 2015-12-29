from hackernews import HackerNews
import json
import numpy as np
import unicodedata

import random
import string
import cherrypy
import Queue
import threading

class article:
    url = ""
    title = ""
    article_id = 0
    article_vector = None
    mod_weight = 0.1

    def __init__(self, url, title, article_id):
        self.url = url
        self.title = title
        self.article_id = article_id

        # create 1000 dimensional row vector, with entries between 0 and 1
        random_vector = np.random.rand(1, 1000)

        # normalize vector
        vec_sum = np.sum(random_vector)
        self.article_vector = random_vector / vec_sum

    # return the article vector in a json friendly format
    def as_dict(self):

        retValue = dict()
        retValue['url'] = self.url
        retValue['title'] = self.title
        retValue['article_id'] = self.article_id
        retValue['article_vector'] = np.array(self.article_vector).tolist()

        return retValue

    # If a user with user_vector as user vector clicks this article then modify the article vector as follows
    def mod_article_vector(self, user_vector):
        user_vector = self.mod_weight * user_vector

        tmp_vector = self.article_vector + user_vector
        tmp_vector = tmp_vector / (1 + self.mod_weight)

        self.article_vector = tmp_vector

class pollArticles:
    cached_articles = dict()
    article_limit = 30

    def getHN_stories(self, article_limit):
        hn = HackerNews()

        articles_to_retrieve = int(article_limit*1.5)
        top_story_ids = hn.top_stories(limit=articles_to_retrieve)

        stories = []
        for story_id in top_story_ids:
            stories.append(hn.get_item(story_id))

        return stories

    def HNstories_toArtList(self, stories, article_limit):
        articles = []
        counter = 0

        for x in stories:
            #print x
            if counter == article_limit:
                break

            unicode_url = x.url
            unicode_title = x.title

            str_url = unicode_url.encode('ascii', 'ignore')
            str_title = unicode_title.encode('ascii', 'ignore')

            if str_url != "":
                new_article = article(str_url, str_title, x.item_id)
                articles.append(new_article)
                counter += 1


        return articles

    def convertArticlesToArtDict(self, articles, cached_articles):
        new_cached_articles = dict()

        for art in articles:
            if art.url in cached_articles:
                new_cached_articles[art.article_id] = cached_articles[art.article_id]
            else:
                new_cached_articles[art.article_id] = art

        return new_cached_articles


    def poll_articles(self):
        hn_stories = self.getHN_stories(self.article_limit)
        hn_articles = self.HNstories_toArtList(hn_stories, self.article_limit)
        self.cached_articles = self.convertArticlesToArtDict(hn_articles, self.cached_articles)

        self.save_articles_to_json()

    def save_articles_to_json(self):
        article_keys = self.cached_articles.keys()

        article_list = []
        for x in article_keys:
            article_object = self.cached_articles[x]
            article_list.append(article_object.as_dict())

        with open('./web/data/top_articles.json', 'w') as outfile:
            json.dump(article_list, outfile)

        print ("LOL")

    #TODO handle the case when the article_id does not exist server side
    def receive_user_action(self, user_vector, article_id):
        if article_id in self.cached_articles:
            article_to_mod = self.cached_articles[article_id]
            article_to_mod.mod_article_vector(user_vector)

            self.cached_articles[article_id] = article_to_mod
            self.save_articles_to_json()

def threadedFunctionality():
    while(True):
        if (!userActions.empty()):
            local_set = userActions.get()
            backEnd.receive_user_action(local_set[0], local_set[1])


class PythonBackEnd(object):
    backEnd = pollArticles()
    backEnd.poll_articles()

    userActions = Queue()
    t = threading.Thread(target=threadedFunctionality())
    t.start()

    exposed = True

    def POST(self, user_vector, article_id):        
        if (int(article_id)):
            userVector = json.loads(user_vector)
            userVector = np.array(userVector)

            print (article_id)
            self.userActions.put([userVector, int(article_id)])
            #self.backEnd.receive_user_action(userVector, int(article_id))

        return

if __name__ == '__main__':
    conf = {
         '/': {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         }
     }
    cherrypy.quickstart(PythonBackEnd(), '/', conf)


#backEnd = pollArticles()
#backEnd.poll_articles()

# test case
#uv = np.zeros((1,1000))
#uv[0,999] = 1
#vvar = 10152735
#backEnd.receive_user_action(uv, vvar)