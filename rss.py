#!/usr/bin/python3
# Created by Yevgeniy Goncharov, https://sys-adm.in
# Script for reading and forwarding to Telegram, rss feeds

# Imports
import sqlite3
import requests
import urllib
import feedparser
import os

# Bot creds
bot_token = 'TOKEN'
bot_chatID = 'CHAT-ID'

# Feeds
myfeeds = [
  'https://sys-adm.in/?format=feed&type=rss',
  'https://forum.sys-adm.in/index.php?action=.xml;type=rss'
]
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
    requests.get(send_text, proxies=proxies)

# Check, read articles
def read_article_feed(feed):
    """ Get articles from RSS feed """
    feed = feedparser.parse(feed)
    for article in feed['entries']:
        if article_is_not_db(article['title'], article['published']):
            add_article_to_db(article['title'], article['published'])
            bot_sendtext('New feed found ' + article['title'] +',' + article['link'])

# Rotate feeds array
def spin_feds():
    for x in myfeeds:
        read_article_feed(x)

# Runner :)
if __name__ == '__main__':
    spin_feds()
    # get_posts()
    db_connection.close()

