import requests
import re
import dataset
from bs4 import BeautifulSoup

def make_request(url):
    '''makes a request and returnst it.'''
    print('[*] Getting {}'.format(url))
    return requests.get(url)

def get_pages(url):
    request = make_request(url)
    bs = BeautifulSoup(request.text, 'lxml')
    pager = bs.find('ul', {'class':'pager'})
    next_page_rel_link = bs.find('li',
            {'class':'next'}).contents[1]
    pages = []

    while next_page_rel_link:
        href = next_page_rel_link.get('href')
        pages.append(url + href.strip('/'))
        try:
            request = make_request(pages[-1])
            bs = BeautifulSoup(request.text, 'lxml')
            pager = bs.find('ul', {'class':'pager'})
            next_page_rel_link = bs.find('li',
                    {'class':'next'}).contents[1]
        except AttributeError:
            break
    return pages

def get_quotes_data(request, main_url, authors, db):
    '''gets all the quotes info in the BeautifulSoup object bs_div.'''

    # html = make_request(url).text
    bs = BeautifulSoup(request.text, 'lxml')

    divs = bs.find_all('div', {'class':'col-md-8'})
    for div in divs:
        if div.find('div', {'class':'quote'}) != None:
            for quote in div.find_all('div', {'class':'quote'}):
                text = quote.find('span', {'class':'text'}).get_text()
                author = quote.find('small', {'class':'author'}).get_text()
                if author not in authors:
                    # add author to the set has a dict
                    # {author: {date, place, description}
                    author_data = get_author_info(quote, request, main_url)
                    author_id = len(authors)
                    authors.add(author)
                    author_data.update({'author_id':author_id})
                    db['authors'].insert(author_data)
                tags, tags_links = get_tags(quote, main_url)

                # Save all the data in the dataset object
                quote_id = db['quotes'].insert({'text':text,
                                                'author':author})
                db['quote_tags'].insert_many(
                    [{'quote_id':quote_id, 'tag_id':tag} for tag in tags_links]
                )
                print('[*] Quote scraped.')
    return True

def get_author_info(bs, request, main_url):
    '''gets a BeautifulSoup object and looks for the "about" link,
    visits the url and scrape the author info.'''
    author_href = bs.find('a', href=re.compile(
        '/author/[a-zA-z]*\-[a-zA-Z]')).get('href')
    author_url = main_url + author_href
    author_html = make_request(author_url).text
    print('[*] Getting {}'.format(author_url))

    author_bs = BeautifulSoup(author_html, 'lxml')
    data = author_bs.find('div', {'class':'author-details'})
    author_born_date = data.find('span', 
                {'class':'author-born-date'}).get_text()
    author_born_location = data.find('span',
                {'class':'author-born-location'}).get_text().replace('in ', '')
    author_description = data.find('div',
                         {'class':'author-description'}).get_text()
    author_data = {'birth_place':author_born_location,
                   'birth_date':author_born_date,
                   'description':author_description}
    print('[*] Author data scraped.')
    return author_data

def get_tags(bs, main_url):
    '''gets a BeautifulSoup object and looks for the tags.'''
    tags = []
    tags_links = []
    tag_list = bs.find('div', {'class':'tags'})
    for t in tag_list.find_all('a', {'class':'tag'}):
        tags.append(t.get_text())
        tags_links.append(main_url + t.get('href'))
    print('[*] Tags scraped.')
    return tags, tags_links

if __name__ == '__main__':
    main_url = 'http://quotes.toscrape.com/'
    db = dataset.connect('sqlite:///quotes.db')
    authors = set()
    request = make_request(main_url)

    pages_to_scrape = [main_url]
    for page in get_pages(main_url):
        pages_to_scrape.append(page)
    
    for page in pages_to_scrape:
        get_quotes_data(request, main_url, authors, db)