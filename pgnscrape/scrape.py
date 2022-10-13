#!/usr/bin/env python
import os
import json
import time
import requests
import bs4
from bs4 import BeautifulSoup as BS

url = 'https://www.pgnmentor.com'
main_url = f'{url}/files.html'

png_main = 'main_png_site.html'

def getMainSoup():
    # Fetch file if necessary
    if not os.path.exists(png_main):
        text = requests.get(main_url).text
        soup = BS(text, 'html.parser')
        with open(png_main, 'w') as f:
            f.write(soup.prettify())

    # Load file from disk
    else:
        with open(png_main) as f:
            soup = BS(f, 'html.parser')

    return soup

# Locates specific openings table within input soup object
def getOpeningsTable(soup):
    # jump close to the table we want
    curr = soup.find(id='modking')

    attempts = 0
    while True:
        if attempts > 10:
            raise RuntimeError('could not find modern king openings table')

        curr = curr.next

        # Ignore text-only tags
        if isinstance(curr, bs4.element.NavigableString):
            continue 

        attempts += 1

        if curr.name == 'table':
            return curr

def process_row(row):
    tds = row.find_all('td')
    assert len(tds) == 3

    link = tds[0].find('a')['href']
    if 'sici' not in link.lower():
        return

    return f'{url}/{link}'

def getLinks(table):
    ret = []
    for row in table.find_all('tr'):
        if link := process_row(row):
            ret.append(link)
    return ret

def downloadAll(links):
    sleep_time = 2
    for link in links:
        r = requests.get(link)
        r.raise_for_status()
        with open(os.path.basename(link), 'wb') as f:
            f.write(r.content)
        time.sleep(sleep_time)
    print(f'(sleep time: {sleep_time*len(links)})')

def main():
    soup = getMainSoup()
    table = getOpeningsTable(soup)
    sicilian_links = getLinks(table)
    downloadAll(sicilian_links)

if __name__ == '__main__':
    main()
