from hackernews import HackerNews
import json
import numpy as np
import unicodedata

class article:
    url = ""
    title = ""
    article_vector = None

    def __init__(self, url, title):
        self.url = url
        self.title = title
        random_vector = np.random.rand(1000, 1)
        vec_sum = np.sum(random_vector)
        article_vector = random_vector / vec_sum


hn = HackerNews()

top_story_ids = hn.top_stories(limit=30)

stories = []
for story_id in top_story_ids:
    stories.append(hn.get_item(story_id))

for x in stories:
    print x.title, x.url

articles = []
json_list = []
#for x in stories:
#    unicode_url = x.url
#    unicode_title = x.title

#    str_url = unicode_url.encode('ascii', 'ignore')
#    str_title = unicode_title.encode('ascii', 'ignore')

#    new_article = article(str_url, str_title)
#    articles.append(new_article)

for x in articles:
    print x.title

#jj = json_list[0]
#print type(jj['url'])
#print jj['title']
#print jj

