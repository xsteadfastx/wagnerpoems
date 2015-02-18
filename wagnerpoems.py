from bs4 import BeautifulSoup
from urlparse import urljoin
from unidecode import unidecode
from hyphen import Hyphenator
from random import choice
from birdy.twitter import UserClient
import re
import requests

from config import *


def get_daily_post():
    match_url = re.compile(
        'http[s]?://(?:[a-zA-Z]\
        |[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    match_alpha_num = re.compile('\W+')

    r = requests.get(
        'http://www.bild.de/suche.bild.html?query=franz+josef+wagner')
    soup = BeautifulSoup(r.text)

    latest_post_link = [i.get('href')
                        for i in soup.find_all('a')
                        if 'franz' in str(i.get('href'))][0]

    latest_post_link = urljoin('http://bild.de', latest_post_link)

    r = requests.get(latest_post_link)
    soup = BeautifulSoup(r.text)

    post = soup.find_all('div', class_='txt clearfix')[0].find_all('p')

    post = [match_alpha_num.sub(' ', unidecode(i.text)).strip()
            for i in post
            if not re.search(match_url, i.text)][:-4]

    post = ' '.join(post)

    return post


def word_count_dict():
    post = get_daily_post()
    hyph = Hyphenator('de_DE')
    count_dict = {}
    words = post.split(' ')
    for word in words:
        count = len(hyph.syllables(unicode(word)))
        if count not in count_dict:
            count_dict[count] = []
        count_dict[count].append(word)

    return count_dict


def haiku_elements(count_dict, count):
    while True:
        random_choice = [choice(count_dict.keys()), choice(count_dict.keys())]
        if sum(random_choice) == count:
            return random_choice


def create_haiku():
    count_dict = word_count_dict()
    haiku = []

    elements = haiku_elements(count_dict, 5)
    haiku.append('{} {}'.format(
        choice(count_dict[elements[0]]),
        choice(count_dict[elements[1]])))

    elements = haiku_elements(count_dict, 7)
    haiku.append('{} {}'.format(
        choice(count_dict[elements[0]]),
        choice(count_dict[elements[1]])))
    elements = haiku_elements(count_dict, 5)

    haiku.append('{} {}'.format(
        choice(count_dict[elements[0]]),
        choice(count_dict[elements[1]])))

    return ' '.join(haiku)


def send_tweet(tweet):
    client = UserClient(CONSUMER_KEY,
                        CONSUMER_SECRET,
                        ACCESS_TOKEN,
                        ACCESS_TOKEN_SECRET)

    response = client.api.statuses.update.post(status=tweet)
    return response


def main():
    send_tweet(create_haiku())


if __name__ == '__main__':
    main()
