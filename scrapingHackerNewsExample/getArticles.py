import re
import requests
from bs4 import BeautifulSoup

def make_get_request(url):
    '''returns a get request to the given url'''
    r = requests.get(url)
    return r

articles = []
url = 'https://news.ycombinator.com/news'
bs = BeautifulSoup(make_get_request(url).text, 'lxml')
item_list = bs.find('table', {'class':'itemlist'})

# Declare data needed
elements = []

for athing in item_list.find_all('tr', {'class':'athing'}):
    element = {}
    element['title'] = athing.find('a', {'class':'storylink'}).get_text()
    element['link'] = athing.find('a', {'class':'storylink'}).get('href')
    next_row = athing.find_next_sibling('tr')
    element['score'] = next_row.find('span', {'class':'score'}).get_text()
    element['comments'] = next_row.find('a', string=re.compile('\d+&nbsp;|\s'\
    'comments(s?)'))
    element['comments'] = element['comments'].get_text(strip=True).replace(
        '\xa0', ' ') if element['comments'] else '0 comments'
    elements.append(element)

for element in elements:
    for k, v in element.items():
        print('{}: {}'.format(k, v))
    next_i = input('[*] Next Item (n): ')