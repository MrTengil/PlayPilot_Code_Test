import time
import json
import get_viaplay_films


if __name__ == '__main__':
    t1 = time.time()
    max_workers = 20
    films_list = get_viaplay_films.fetch(max_workers)
    t_elapsed = time.time()-t1

    print(f'Done fetching the Viaplay films! \nElapsed time {round(t_elapsed, 3)} seconds')

    with open('Viaplay_films', 'w') as fout:    # Save the films in a file for later use
        json.dump(films_list, fout)



