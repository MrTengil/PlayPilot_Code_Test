import requests
import asyncio
import concurrent.futures


def fetch(max_workers=20):  # max_workers are used to determine how many workers are used when fetching playable links. Too many may trigger Viaplay ddos protection ?
    async def get_all_pages(total_number_pages):
        loop = asyncio.get_event_loop()
        pages_list = []
        futures = [
            loop.run_in_executor(
                None,
                requests.get,
                get_viaplay_film_page_url(page_number)
            )
            for page_number in range(1, total_number_pages + 1)
        ]
        for response in await asyncio.gather(*futures):
            pages_list.append(response.json())
        return pages_list

    async def get_all_playable_links(stream_list, workers):
        loop = asyncio.get_event_loop()
        playable_link_list = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                loop.run_in_executor(
                    executor,
                    requests.get,
                    stream_url
                )
                for stream_url in stream_list
            ]
            for response in await asyncio.gather(*futures):
                playable_link_list.append(
                    response.json()['_embedded']['viaplay:product']['_links']['viaplay:stream']['href'])
            return playable_link_list

    def if_available(item, key):  # Some of the values does not exist so we need to check if it exists before adding it
        if key in item:
            return item[key]

    def get_viaplay_film_page_url(
            page_number):  # requests.get() has pagination built in but I couldn't get it working with paralellization in time so this is my work around...
        return 'https://content.viaplay.se/pcdash-se/film/samtliga?&pageNumber=' + str(page_number)    # This wouldn't work great if the API changed URL...

    film = dict()
    films_list = []
    stream_link_list = []
    first_request_json = requests.get(get_viaplay_film_page_url(1)).json()  # Fetches first page to get number of pages for pagination
    n_pages = first_request_json['_embedded']['viaplay:blocks'][0]['pageCount']
    loop = asyncio.get_event_loop()
    pages_list = loop.run_until_complete(get_all_pages(n_pages))
    for page_number in range(n_pages):
        print(f'Requesting page #{page_number+1}')
        for item in pages_list[page_number]['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:products']:
            if item['type'] == 'movie':
                film['type'] = item['type']
                film['title'] = if_available(item['content'], 'title') or None
                film['description'] = if_available(item['content'], 'synopsis') or None
                film['production_country'] = if_available(item['content']['production'], 'country') or None
                film['year'] = if_available(item['content']['production'], 'year') or None
                film['director'] = if_available(item['content']['people'], 'directors') or None
                film['poster'] = if_available(item['content']['images']['boxart'], 'url') or None

                if 'imdb' in item['content']:  # Not all movies has IMDB data
                    imdb_id = item['content']['imdb']['id']
                else:
                    imdb_id = None
                film['imbd_id'] = imdb_id

                if 'language' in item['content']:  # Same as the IMDB id but with audio languages
                    audio_languages = item['content']['language']['audio']
                else:
                    audio_languages = None
                film['audio_languages'] = audio_languages

                stream_link_list.append(item['_links']['self']['href'])
                films_list.append(film.copy())

    playable_link_list = loop.run_until_complete(get_all_playable_links(stream_link_list, max_workers))
    for index, item in enumerate(films_list):
        films_list[index]['playable_link'] = playable_link_list[index]

    return films_list
