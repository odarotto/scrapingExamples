import requests
import re
import dataset
from bs4 import BeautifulSoup

def make_request(url):
    '''makes a request and returns it.'''
    return requests.get(url)

def get_quotes_data(url):
    '''gets all the quotes info in the BeautifulSoup object bs_div.'''
    html = make_request(url).text
    print('[*] Getting {}'.format(url))
    print('[*] Getting {}'.format(url))
    bs = BeautifulSoup(html, 'lxml')

    quotes_data = []
    divs = bs.find_all('div', {'class':'col-md-8'})
    for div in divs:
        if div.find('div', {'class':'quote'}) != None:
            for quote in div.find_all('div', {'class':'quote'}):
                text = quote.find('span', {'class':'text'}).get_text()
                author = quote.find('small', {'class':'author'}).get_text()
                date_birth, place_birth = get_author_info(quote, url)
                tags, tags_links = get_tags(quote, url)
                quotes_data.append(
                    {
                        'text':text,
                        'author':author,
                        'date of birth':date_birth,
                        'place of birth':place_birth,
                        'tags':tags,
                        'links for tags':tags_links
                    }
                ) 
                print('[*] Quote scraped.')
    return quotes_data

def get_author_info(bs, url):
    '''gets a BeautifulSoup object and looks for the "about" link,
    visits the url and scrape the author info.'''
    author_href = bs.find('a', href=re.compile(
        '/author/[a-zA-z]*\-[a-zA-Z]')).get('href')
    author_url = url + author_href
    author_html = make_request(author_url).text
    print('[*] Getting {}'.format(author_url))

    author_bs = BeautifulSoup(author_html, 'lxml')
    data = author_bs.find('div', {'class':'author-details'})
    author_born_date = data.find('span', 
                {'class':'author-born-date'}).get_text()
    author_born_location = data.find('span',
                {'class':'author-born-location'}).get_text().replace('in ', '')
    print('[*] Author data scraped.')
    return author_born_date, author_born_location

def get_tags(bs, url):
    '''gets a BeautifulSoup object and looks for the tags.'''
    tags = []
    tags_links = []
    tag_list = bs.find('div', {'class':'tags'})
    for t in tag_list.find_all('a', {'class':'tag'}):
        tags.append(t.get_text())
        tags_links.append({t.get_text():url + t.get('href')})
    print('[*] Tags scraped.')
    return tags, tags_links

# def save_data(quote, author, author_DoB, author_PoB):
#     '''receive the text of the quote, its author name, date of birth and
#     place of birth and saves them in a dataset object.'''

if __name__ == '__main__':
    url = 'http://quotes.toscrape.com/'
    data = get_quotes_data(url)
    for quote in data:
        for k, v in quote.items():
            print('{}: {}'.format(k, v))