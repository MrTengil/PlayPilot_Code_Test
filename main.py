import requests

class film:
    def __init__(self, title, description, audio_languages, production_country, year, director, poster, imdb_id, playable_link):
        self.title = title
        self.description = description
        self.audio_languages = audio_languages
        self.production_country = production_country
        self.year = year
        self.director = director
        self.poster = poster
        self.imdb_id = imdb_id
        self.playable_link = playable_link




if __name__ == '__main__':
    url = 'https://content.viaplay.se/pcdash-se/film/samtliga?&pageNumber='
    r = requests.get(url + '1')
    r_json = r.json()
    n_pages = r_json['_embedded']['viaplay:blocks'][0]['pageCount']
    total_products = r_json['_embedded']['viaplay:blocks'][0]['totalProductCount']
    films_list = [None]*total_products
    for page in range(1, n_pages+1):
        r = requests.get(url + str(page))
        r_json = r.json()
        for index, item in enumerate(r_json['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:products']):
            if item['type'] == 'movie':
                if ('title' in item['content']):
                    title = item['content']['title']
                else:
                    title = 'N/A'
                if ('synopsis' in item['content']):
                    description = item['content']['synopsis']
                else:
                    description = 'N/A'
                if ('language' in item['content']):
                    audio_languages = item['content']['language']['audio']
                else:
                    audio_languages = 'N/A'


                if ('country' in item['content']['production']):
                    production_country = item['content']['production']['country']
                else:
                    production_country = 'N/A'
                if ('year' in item['content']['production']):
                    year = item['content']['production']['year']
                else:
                    year = 'N/A'
                if ('directors' in item['content']['people']):
                    director = item['content']['people']['directors']
                else:
                    director = 'N/A'
                if ('imdb' in item['content']):
                    imdb_id = item['content']['imdb']['id']
                else:
                    imdb_id = 'N/A'

                if ('url' in item['content']['images']['boxart']):
                    poster = item['content']['images']['boxart']['url']
                else:
                    poster = 'N/A'

                # Följande bit av kod används för att komma åt play-länken
                # Den ökar körtiden för scriptet från o(n) till o(n^2) där n är totala antalet filmer
                self_url = item['_links']['self']['href']
                r_self = requests.get(self_url)
                r_self_json = r_self.json()
                playable_link = r_self_json['_embedded']['viaplay:product']['_links']['viaplay:stream']['href']


                films_list[index] = film(title, description, audio_languages, production_country, year, director, poster, imdb_id, playable_link)


    boll = 0

