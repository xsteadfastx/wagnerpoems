from bs4 import BeautifulSoup
from urllib.parse import urljoin
from hyphen import Hyphenator
from birdy.twitter import UserClient
from itertools import permutations
import re
import requests
import random

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

    post = [match_alpha_num.sub(' ', i.text).strip()
            for i in post
            if not re.search(match_url, i.text)][:-4]

    post = ' '.join(post)

    return post


def syllable_count(word):
    hyph = Hyphenator('de_DE')
    return len(hyph.syllables(word))


def word_tuple(word_list):
    tuple_list = []
    for word in word_list:
        syll = syllable_count(word)
        if syll == 0:
            syll = 1
        tuple_list.append((word, syll))

    return tuple_list


def haiku_elements(words, syllcount):
    word_length = list(range(1, 5))
    random.shuffle(word_length)
    random.shuffle(words)
    for length in word_length:
        perms = permutations(words, r=length)

        for perm in perms:
            if sum([i[1] for i in perm]) == syllcount:
                return [i[0].lower() for i in perm]


def create_haiku():
    post = get_daily_post()
    words = word_tuple(post.split())

    haiku = []
    haiku.append(' '.join(haiku_elements(words, 5)))
    haiku.append(' '.join(haiku_elements(words, 7)))
    haiku.append(' '.join(haiku_elements(words, 5)))

    return '\n'.join(haiku)


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
