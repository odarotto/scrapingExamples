import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

main_url = 'http://www.imdb.com/title/tt0944947/episodes'

episodes = []
ep_ratings = []

for season in range(1, 9):
    r = requests.get(main_url, params={'season':season})
    bs = BeautifulSoup(r.text, 'lxml')
    ep_listing = bs.find('div', {'class':'eplist'})
    for ep_number, div \
        in enumerate(ep_listing.find_all('div', recursive=False)):
        episode = '{}.{}'.format(season, ep_number + 1)
        rating_el = div.find(class_='ipl-rating-star__rating')
        rating = float(rating_el.get_text(strip=True))
        print('Episode: {} -- rating: {}'.format(episode, rating))
        episodes.append(episode)
        ep_ratings.append(rating)


episodes = ['S' + e.split('.')[0] if int(e.split('.')[1]) == 1 else '' \
            for e in episodes]
plt.figure()
positions = [a*2 for a in range(len(ep_ratings))]
plt.bar(positions, ep_ratings, align='center')
plt.xticks(positions, episodes)
plt.show()