from hackernews import HackerNews
import json
import numpy as np
import unicodedata

class article:
    url = ""
    title = ""
    id = 0
    article_vector = None

    def __init__(self, url, title, id):
        self.url = url
        self.title = title
        self.id = id

        # create 1000 dimensional row vector, with entries between 0 and 1
        random_vector = np.random.rand(1, 1000)

        # normalize vector
        vec_sum = np.sum(random_vector)
        self.article_vector = random_vector / vec_sum

    def as_dict(self):

        retValue = dict()
        retValue['url'] = self.url
        retValue['title'] = self.title
        retValue['id'] = self.id
        retValue['article_vector'] = np.array(self.article_vector).tolist()

        return retValue

def getHN_stories(article_limit):
    hn = HackerNews()

    articles_to_retrieve = int(article_limit*1.5)
    top_story_ids = hn.top_stories(limit=articles_to_retrieve)

    stories = []
    for story_id in top_story_ids:
        stories.append(hn.get_item(story_id))

    return stories

def HNstories_toArtList(stories, article_limit):
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

def convertArticlesToArtDict(articles, cached_articles):
    new_cached_articles = dict()

    for art in articles:
        if art.url in cached_articles:
            new_cached_articles[art.id] = cached_articles[art.id]
        else:
            new_cached_articles[art.id] = art

    return new_cached_articles


def mainScript():
    article_limit = 30
    cached_articles = dict()

    hn_stories = getHN_stories(article_limit)
    hn_articles = HNstories_toArtList(hn_stories, article_limit)
    cached_articles = convertArticlesToArtDict(hn_articles, cached_articles)

    article_keys = cached_articles.keys()

    article_list = []
    for x in article_keys:
        article_object = cached_articles[x]
        article_list.append(article_object.as_dict())

    with open('top_articles.json', 'w') as outfile:
        json.dump(article_list, outfile)

'''
    for x in l:
        with open('top_articles.json', 'w') as outfile:
            article_object = cached_articles[x]
            json.dump(article_object.as_dict(), outfile)
'''

mainScript()