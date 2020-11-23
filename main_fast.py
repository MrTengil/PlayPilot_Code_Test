import requests
import asyncio
import concurrent.futures
import time


class film:
    def __init__(self, title, description, audio_languages, production_country, year, director, poster, imdb_id, playable_link = None):
        self.title = title
        self.description = description
        self.audio_languages = audio_languages
        self.production_country = production_country
        self.year = year
        self.director = director
        self.poster = poster
        self.imdb_id = imdb_id
        self.playable_link = playable_link


    def update_playable_link(self, playable_link):
        self.playable_link = playable_link


def get_page_url(page_number):
    return 'https://content.viaplay.se/pcdash-se/film/samtliga?&pageNumber=' + str(page_number)


async def get_all_pages(total_number_pages):
    loop = asyncio.get_event_loop()
    pages_list = []
    futures = [
        loop.run_in_executor(
            None,
            requests.get,
            get_page_url(page_number)
        )
        for page_number in range(1, total_number_pages + 1)
    ]
    for response in await asyncio.gather(*futures):
        pages_list.append(response.json())
    return pages_list


async def get_all_playable_links(stream_list):
    loop = asyncio.get_event_loop()
    playable_link_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            loop.run_in_executor(
                executor,
                requests.get,
                stream_url
            )
            for stream_url in stream_list
        ]
        for response in await asyncio.gather(*futures):
            playable_link_list.append(response.json()['_embedded']['viaplay:product']['_links']['viaplay:stream']['href'])
        return playable_link_list


if __name__ == '__main__':
    t1 = time.time()
    films_list = []
    first_request_json = requests.get(get_page_url(1)).json()  # Fetches first page to get number of pages for pagination
    n_pages = first_request_json['_embedded']['viaplay:blocks'][0]['pageCount']
    loop = asyncio.get_event_loop()
    pages_list = loop.run_until_complete(get_all_pages(n_pages))
    stream_list = []
    for page_number in range(n_pages):
        print(f'Requesting page #{page_number}')
        for item in pages_list[page_number]['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:products']:
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

                stream_list.append(item['_links']['self']['href'])
                films_list.append(
                    film(title, description, audio_languages, production_country, year, director, poster, imdb_id))
    playable_link_list = loop.run_until_complete(get_all_playable_links(stream_list))
    for index, item in enumerate(films_list):
        item.update_playable_link(playable_link_list[index])
    t2 = time.time()
    print(f'Elapsed time {t2-t1} seconds')
    boll = 0