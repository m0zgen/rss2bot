#!/usr/bin/env python3
# Created by Yevgeniy Goncharov, https://sys-adm.in
# Script for reading and forwarding to Telegram, rss feeds

# Imports
import sqlite3
import requests
import feedparser
import os
import urllib
import random

# Bot creds
bot_token = 'TOKEN'
bot_chatID = 'CHAT_ID'

# Feeds
myfeeds = [
  'https://forum.sys-adm.in/latest.rss',
]

# User agents
uags = [
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
]

# Random User Agent (from uags list)
ua = random.choice(uags)

# Header
headers = {
  "Connection" : "close",  # another way to cover tracks
  "User-Agent" : ua
}

# Proxies
proxies = {
}

# DB
scriptDir = os.path.dirname(os.path.realpath(__file__))
db_connection = sqlite3.connect(scriptDir + '/rss.sqlite')
db = db_connection.cursor()
db.execute('CREATE TABLE IF NOT EXISTS myrss (title TEXT, date TEXT)')

# Get posts from DB and print
def get_posts():
    with db_connection:
        db.execute("SELECT * FROM myrss")
        print(db.fetchall())

# Check post in DB
def article_is_not_db(article_title, article_date):
    db.execute("SELECT * from myrss WHERE title=? AND date=?", (article_title, article_date))
    if not db.fetchall():
        return True
    else:
        return False

# Add post to DB
def add_article_to_db(article_title, article_date):
    db.execute("INSERT INTO myrss VALUES (?,?)", (article_title, article_date))
    db_connection.commit()

# Send notify to Telegram bot
def bot_sendtext(bot_message):
    bot_message = urllib.parse.quote(bot_message)
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    requests.get(send_text, proxies=proxies, headers=headers)
    print(send_text)

# Check, read articles
def read_article_feed(feed):
    """ Get articles from RSS feed """
    feedparser.USER_AGENT = ua
    feed = feedparser.parse(feed)
    print(feed)
    for article in feed['entries']:
        if article_is_not_db(article['title'], article['published']):
            add_article_to_db(article['title'], article['published'])
            bot_sendtext('New feed found ' + article['title'] +', ' + article['link'] + ', ' + article['description'])
            print(article)

# Rotate feeds array
def spin_feds():
    for x in myfeeds:
        print(x)
        read_article_feed(x)

# Runner :)
if __name__ == '__main__':
    spin_feds()
    # get_posts()
    db_connection.close()

