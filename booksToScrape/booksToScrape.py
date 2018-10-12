import requests
import dataset
import re
from datetime import datetime
from bs4 import BeautifulSoup

def make_GET_request(url):
    '''makes a GET request using requests library.'''
    r = requests.get(url)
    return r

def next_page(html, base_url):
    '''looks for the next page relative link and returns it'''
    bs = BeautifulSoup(html, 'lxml')
    next_page_abs_link = bs.find('a', string='next').get('href')
    next_page_abs_link
    return next_page_abs_link

def get_books_grid_links(request, url, db):
    '''receive a request and a url and return a list containing all the
    links to the books.'''

    base_url = url
    html = request.text
    next_page_link = ''
    page = 1
    current_url = ''
    while True:
        if next_page_link:
            current_url = base_url + next_page_link
        else:
            current_url = base_url

        html = make_GET_request(current_url).text
        bs = BeautifulSoup(html, 'lxml')
        books_grid = bs.find('ol', {'class':'row'}) 

        for book in books_grid.find_all('article', {'class':'product_pod'}):
            if page >= 2:
                link = base_url + 'catalogue/' + book.find('a').get('href')
            else:
                link = base_url + book.find('a').get('href')
            db['books'].upsert({'book_id': link,
                        'last_seen':datetime.now()},
                        ['book_id'])
            print('[*] Getting {}'.format(link))
        
        # Lets assure that there is a 'next' page
        try:
            next_page_link = next_page(html, base_url)
            page += 1
            # We add 'catalogue' to the path if needed
            if page < 2 or page >= 3:
                next_page_link = 'catalogue/' + next_page_link
            print('Page {}'.format(page))
        except AttributeError:
            break
    return True

def scrape_book(url, bs, db):
    '''receive a book url and scrape all the information needed.
    Then it saves it in the database'''

    main = bs.find(class_='product_main')
    book = {}
    book['book_id'] = url
    book['title'] = main.find('h1').get_text(strip=True)
    book['price'] = main.find(class_='price_color').get_text(strip=True)
    book['instock'] = main.find(class_='availability').get_text(strip=True)
    book['rating'] = ' '.join(main.find(class_='star-rating') \
                        .get('class')).replace('star-rating', '').strip()
    book['img'] = bs.find(class_='thumbnail').find('img').get('src')
    description = bs.find(id='product_description')
    if description:
        book['description'] = description.find_next_sibling('p') \
                                .get_text(strip=True)
    product_info = bs.find('table', {'class':'table-striped'})
    for row in product_info.find_all('tr'):
        header = row.find('th').get_text(strip=True)
        # Cleaning header since it'll be a column in the SQLite
        header = re.sub('[^a-zA-Z]+', ' ', header)
        value = row.find('td').get_text(strip=True)
        book[header] = value
    db['book_info'].upsert(book, ['book_id'])
    print('{} scraped.'.format(book['title']))


if __name__ == '__main__':
    main_url = 'http://books.toscrape.com/'

    db = dataset.connect('sqlite:///books.db')
    request = make_GET_request(main_url)
    get_books_grid_links(request, main_url, db)
    books_links = db['books'].find(order_by=['last_seen'])
    
    for book in books_links:
        link = book['book_id']
        bs = BeautifulSoup(make_GET_request(link).text, 'lxml')
        scrape_book(link, bs, db)
        