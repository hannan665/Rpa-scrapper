from nytimes_news.scrapper import NYTimesNewsScrapper

nytimes_scrapper = NYTimesNewsScrapper()
nytimes_scrapper.start_process()

from reddit.scrapper import RedditScrapper
reddit_obj = RedditScrapper()
reddit_obj.start_process()
