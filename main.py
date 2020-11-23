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

def get_page_url(page_number):
    return 'https://content.viaplay.se/pcdash-se/film/samtliga?&pageNumber=' + str(page_number)



if __name__ == '__main__':
    first_request_json = requests.get(get_page_url(1)).json()   # Fetches first page to get number of pages for pagination
    n_pages = first_request_json['_embedded']['viaplay:blocks'][0]['pageCount']
    total_products = first_request_json['_embedded']['viaplay:blocks'][0]['totalProductCount']
    films_list = []*total_products
    for page in range(1, n_pages+1):
        print(f'Requesting page #{page}')
        page_json = requests.get(get_page_url(page)).json()
        for item in page_json['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:products']:
            if item['type'] == 'movie':

                if ('title' in item['content']):
                    title = item['content']['title'] or 'N/A'
                else:
                    title = None

                if ('synopsis' in item['content']):
                    description = item['content']['synopsis']
                else:
                    description = None
                if ('language' in item['content']):
                    audio_languages = item['content']['language']['audio']
                else:
                    audio_languages = None


                if ('country' in item['content']['production']):
                    production_country = item['content']['production']['country']
                else:
                    production_country = None
                if ('year' in item['content']['production']):
                    year = item['content']['production']['year']
                else:
                    year = None
                if ('directors' in item['content']['people']):
                    director = item['content']['people']['directors']
                else:
                    director = None
                if ('imdb' in item['content']):
                    imdb_id = item['content']['imdb']['id']
                else:
                    imdb_id = None

                if ('url' in item['content']['images']['boxart']):
                    poster = item['content']['images']['boxart']['url']
                else:
                    poster = None

                # Antalet requests ökar drastiskt här för att vi gör en request per film.
                self_url = item['_links']['self']['href']
                r_self_json = requests.get(self_url).json()
                playable_link = r_self_json['_embedded']['viaplay:product']['_links']['viaplay:stream']['href']


                films_list.append(film(title, description, audio_languages, production_country, year, director, poster, imdb_id, playable_link))


    boll = 0

