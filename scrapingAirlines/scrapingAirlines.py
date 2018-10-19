import time
import requests
import pandas
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait  
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


url = 'http://www.iata.org/publications/Pages/code-search.aspx'

def get_results(airline_name):
    '''
    Receives an airline name and returns the info associated to it.
    '''

    session = requests.Session()
    # Remember to spoof the user agent as a precaution
    session.headers.update({
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0'
    })
    r = session.get(url)
    with open('noquery.html', 'w') as f:
        if f.writable():
            f.write(r.text)
    html_soup = BeautifulSoup(r.text, 'lxml')
    form = html_soup.find(id='aspnetForm')
    data = {}
    for inp in form.find_all(['input', 'select']):
        name = inp.get('name')
        value = inp.get('value')
        if not name:
            continue
        if 'ddlImLookingFor' in name:
            value = 'ByAirlineName'
            print('a')
        if 'txtSearchCriteria' in name:
            value = airline_name
            print('b')
        data[name] = value if value else ''

    print('[*] Printing data collected:')
    for k, v in data.items():
        print('{}: {}'.format(k, v))

    response = session.post(url, data=data)
    print(response.status_code)
    html_soup = BeautifulSoup(response.text, 'lxml')
    time.sleep(5)
    with open('content.html', 'w') as f:
        if f.writable():
            f.write(response.text)
    table = html_soup.find('table', {'class':'datatable'})
    if table:
        print('[*] Table found.')
        df = pandas.read_html(str(table))
        return df
    else:
        return False

df = get_results('lufthansa')
print(df)

# # Create new Selenium driver
# caps = DesiredCapabilities().FIREFOX
# caps['marionette'] = True
# nightly_binary = FirefoxBinary('/usr/bin/firefox-nightly')
# options = webdriver.FirefoxOptions()
# options.add_argument('-headless')
# driver = webdriver.Firefox(capabilities=caps, 
#             executable_path='/usr/bin/geckodriver', options=options, firefox_binary=nightly_binary)
# # driver = webdriver.Chrome(executable_path='chromedriver')
# # driver.get('https://www.amazon.com/'\
# #             'Name-Wind-Patrick-Rothfuss/dp/0756404746/'\
# #             'ref=sr_1_1?ie=UTF8&qid=1538436032&sr=8-1&keywords=name+of+the+wind#reader_0756404746')
# def get_results(airline_name):
#     driver.get(url)
#     form_div = driver.find_element_by_css_selector('div.iataStandardForm.narrower')
#     select = Select(form_div.find_element_by_css_selector('select'))
#     select.select_by_value('ByAirlineName')
#     text = form_div.find_element_by_css_selector('input[type=text]')
#     text.send_keys(airline_name)
#     submit = form_div.find_element_by_css_selector('input[type=submit]')
#     submit.click()
#     # table = driver.find_element_by_css_selector('table.datatable')
#     table = driver.find_element_by_class_name('datatable')
#     table_html = table.get_attriute('outerHTML')
#     df = pandas.read_html(str(table_html))
#     return df

# df = get_results('Lufthansa')
# print(df)
# driver.quit()

# We work with requests.session()
# session = requests.Session()
# # Set the user agent as a precaution
# session.headers.update({
#     'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0'
# })

# r = session.get(url)
# html_soup = BeautifulSoup(r.text, 'html.parser')
# form = html_soup.find(id='aspnetForm')

# # Next we get form fields
# data = {}
# for inp in form.find_all(['input', 'select']):
#     name = inp.get('name')
#     value = inp.get('value')
#     if not name:
#         continue
#     data[name] = value if value else ''

# for name in data.keys():
#     # Search by
#     if 'ddlImLookingFor' in name:
#         data[name] = 'ByAirlineName'
#     # Airline name
#     if 'txtSearchCriteria' in name:
#         data[name] = 'lufthansa'

# r = session.post(url, data=data)
# html_soup = BeautifulSoup(r.text, 'lxml')
# table = html_soup.find_all('table', class_='datatable')
# if table:
#     print('table found')
# else:
#     print('table not found')

