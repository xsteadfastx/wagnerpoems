from bs4 import BeautifulSoup
from urllib.parse import urljoin
from hyphen import Hyphenator
from birdy.twitter import UserClient
from itertools import permutations
from random import choice
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


def haiku_elements(syllcount, perms):
    possibles = []
    for perm in perms:
        if perm[0][1] + perm[1][1] == syllcount:
            possibles.append('{} {}'.format(perm[0][0],
                                            perm[1][0]))

    return choice(possibles)


def create_haiku():
    post = get_daily_post().split()
    perms = list(permutations(word_tuple(post), r=2))

    haiku = []
    haiku.append(haiku_elements(5, perms))
    haiku.append(haiku_elements(7, perms))
    haiku.append(haiku_elements(5, perms))

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
