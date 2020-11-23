import requests
import asyncio
import concurrent.futures
import time
import json


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


def if_available(item, key):
    if key in item:
        return item[key]


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
                title = if_available(item['content'], 'title') or None
                description = if_available(item['content'], 'synopsis') or None
                production_country = if_available(item['content']['production'], 'country') or None
                year = if_available(item['content']['production'], 'year') or None
                director = if_available(item['content']['people'], 'directors') or None
                poster = if_available(item['content']['images']['boxart'], 'url') or None

                if ('imdb' in item['content']):     # Not all movies has IMDB rating so we need to check if it exists before getting the id
                    imdb_id = item['content']['imdb']['id']
                else:
                    imdb_id = None

                if ('language' in item['content']): # Same as the IMDB id but with audio languages
                    audio_languages = item['content']['language']['audio']
                else:
                    audio_languages = None

                stream_list.append(item['_links']['self']['href'])
                films_list.append(
                    film(title, description, audio_languages, production_country, year, director, poster, imdb_id))

    playable_link_list = loop.run_until_complete(get_all_playable_links(stream_list))
    for index, item in enumerate(films_list):
        item.update_playable_link(playable_link_list[index])
    t2 = time.time()
    print(f'Elapsed time {t2-t1} seconds')


