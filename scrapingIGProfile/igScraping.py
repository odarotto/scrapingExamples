import time
import re
import subprocess
import requests
import shutil
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

# TODO 
# Optimize image scraping
# Add command line utilities
# Private profile scraping
# Video downloads

def initializeDriver(url):
    '''gets an URL and initialize a driver open and loaded'''
    # Create new Selenium Driver
    caps = DesiredCapabilities().FIREFOX
    caps['marionette'] = True
    nightly_binary = FirefoxBinary('/usr/bin/firefox-nightly')
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')
    driver = webdriver.Firefox(capabilities=caps, 
        executable_path='/usr/bin/geckodriver',
        options=options,
        firefox_binary=nightly_binary)
    return driver

def isPrivate(driver, url):
    '''Checks if the "This is a private account" string appears
    on the profile'''

    print('[*] Checking if account is private')
    driver.get(url)
    try:
        private = driver.find_element_by_tag_name('h2').text
        if private:
            print('[*] {}'.format(private))
            return True
    except TimeoutException:
        print('[*] Timeout!')
        return None
    except NoSuchElementException:
        print('[*] Public Account')
        return False

def scrapePosts(driver, url):
    '''Scrape the links for the posts in the account'''
    links = driver.find_elements_by_xpath('//a[starts-with(@href, "/p/")]')
    urls = set()
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);")
    limit = int(driver.find_element_by_class_name('g47SY ').text)

    while len(urls) < limit:
        links = driver.find_elements_by_xpath(
            '//a[starts-with(@href, "/p/")]')
        for link in links:
            try:
                divs = link.find_elements_by_tag_name('div')
                media_link = ''
                if len(divs) == 5:
                    media_link = link.get_attribute('href')
                    t = ('V', media_link)
                    if t not in urls:
                        urls.add(t)
                        print('{} added'.format(media_link))
                else:
                    media_link = link.find_element_by_class_name('KL4Bh')\
                        .find_element_by_tag_name('img')
                    t = ('I', media_link.get_attribute('src'))
                    if t not in urls:
                        urls.add(t)
                        print('{} added'.format(media_link.get_attribute('src')\
                            .split('/')[-1]))
            except StaleElementReferenceException:
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        reachBottom = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
    return urls

def downloadContent(driver, urls):
    '''Download the content from the urls according with the
    download option.'''

    print('[!] I have collected all the posts\' links.')
    download_option = input('[!] Do you want the links in a .txt file or want'\
    'me to download the images for you?(f:file, l:links):')

    print('[!] Sorting URLs')
    urls = sorted(urls)
    image_urls = [url for url in urls if url[0]=='I']
    video_posts = [url for url in urls if url[0]=='V']

    if download_option == 'f':
        # Scrape image's links and download images
        # for url in image_urls:
        #     downloadImage(url)
        for url in video_posts:
            downloadVideo(driver, url)
    elif download_option == 'l':
        return urls
    else:
        print('[!] Please enter a valid option')
        pass

def downloadVideo(driver, url):
    '''Opens a driver and downloads the video from post'''
    link = url[-1]
    driver.get(link)
    time.sleep(3)
    html = driver.find_element_by_tag_name('html').get_attribute('innerHTML')
    bs = BeautifulSoup(html, 'lxml')

    video_links = bs.find('article').find('div', {'class':'_97aPb wKWK0'})\
        .find_all('div')
    for video in video_links:
        if video.get('class') == '_5wCQW':
            # video.find()
            video_link = video.find('video').get('src')
    # video_link = driver.find_element_by_class_name('OAXCp ')\
    #         .find_element_by_tag_name('video').get_attribute('src')
    r = requests.get(video_link, stream=True)
    filename = ''
    if r.status_code == 200:
        filename = link.split('/')[-1]
        with open(filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    print('{} saved'.format(filename))

def downloadImage(url):
    '''Download an image from url'''
    link = url[-1]
    r = requests.get(link, stream=True)
    filename = ''
    if r.status_code == 200:
        filename = link.split('/')[-1]
        with open(filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    print('{} saved'.format(filename))


def logIn(driver):
    '''Ask the user for login credentials and make the login'''
    pass

if __name__ == '__main__':
    url = 'https://www.instagram.com/noemiewolfs/'
    driver = initializeDriver(url)
    driver.get(url)
    print('[*] Opening {}'.format(url))

    try:
        profile_name = WebDriverWait(driver, 10).until(
            expected.presence_of_element_located((By.TAG_NAME, 'h1'))
        ).text
        print('[*] Profile name: {}, loaded!'.format(profile_name), sep=' ')

        if isPrivate(driver, url):
            # Ask if the user account follows the target account
            answer = input('Do you follow the target account on Instagram?(y/n): ')

            # Send form login
            if answer == 'y':
                pass
            else:
                pass
            # Scrape images directly
            posts_urls = scrapePosts(driver, url)
            pass
        else:
            # Scrape images directly
            posts_urls = scrapePosts(driver, url)
            pass
        downloadContent(driver, posts_urls)
    finally:
        driver.close()