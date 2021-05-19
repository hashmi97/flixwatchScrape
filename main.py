import requests
from bs4 import BeautifulSoup
import os
import traceback
import pandas as pd
import sys
import numpy as np
import argparse
from datetime import datetime


# This method pulls the list of available countries from the website and
# there is a bug at the moment where Mongolia is missing on the website which
# is why I have it hardcoded
def get_list_of_countries():
    country_url = 'https://www.flixwatch.co/catalogs/'
    country_res = requests.get(country_url)
    country_html_page = country_res.content
    country_soup = BeautifulSoup(country_html_page, 'html.parser')
    countries = np.array([])
    for web_line in country_soup.find_all(text=True):
        if web_line.parent.name in ['a', 'details']:
            countries = np.append(countries, (web_line.parent.name, web_line))
    countries = countries[np.min(np.where(countries == 'details')):
                          np.max(np.where(countries == 'details'))]
    countries = countries[np.logical_and(
        countries != 'details', np.logical_and(countries != 'a', countries !=
                                               '\n'))]
    countries = np.append(countries, 'Mongolia')
    np.unique(countries).sort()
    return countries


# This method gets the maximum number page. It is set as 50 for countries right
# now but in the case it gets changed or increased then the number is updated
# here.
def get_max_page_num():
    page_num_url = 'https://www.flixwatch.co/catalogue/netflix-usa'
    page_num_res = requests.get(page_num_url)
    page_num_html_page = page_num_res.content
    page_num_soup = BeautifulSoup(page_num_html_page, 'html.parser')
    max_page_n = 0
    for line in page_num_soup.find_all(text=True):
        if line.parent.name == 'a':
            if 'Next' in line:
                break
            max_page_n = line
    return max_page_n


# This method parses every show page and extracts the following (Name,
# description, genre, alternative genres, streaming countries, IMDB and
# metacritic scores if they exist, whether the show is family friendly, year it
# was released, age restrictions and audio language) to the dataframe.
def parse_show_page(array, show_type):
    global df, log_file
    array = array[11:-5]
    show_name = array[0]
    print(datetime.now().strftime('[%d/%m/%Y %H:%M:%S]: ') +
          'Now working on show {}'.format(show_name), file=log_file)
    print(datetime.now().strftime('[%d/%m/%Y %H:%M:%S]: ') +
          'Now working on show {}'.format(show_name))
    show_description = array[2]
    show_genre = ''.join(
        array[np.where(array == 'Genre:')[0] + 1]).strip()
    show_alt_genre = ''.join(array[np.where(
        array == 'Alternate Genre:')[0] + 1]).strip()
    show_streaming_countries = ''
    i = np.where(array == 'Streaming in:')[0] + 1
    while array[i] != 'IMDb:':
        show_streaming_countries = (show_streaming_countries +
                                    str(array[i][0])).strip()
        i += 1
    show_IMDb_score = array[
        np.where(array == 'IMDb:')[0] + 1][0].strip()
    show_metacritic_score = array[np.where(
        array == 'Metacritic:')[0] + 1][0].strip()
    show_age_restriction = array[
        np.where(array == 'Suitable for Age ')[0] + 3][0]
    show_family_friendly = array[
        np.where(array == 'Family Friendly:')[0] + 1][0].strip()
    show_year = int(
        array[np.where(array == 'Year:')[0] + 1])
    show_audio = array[np.where(array == 'Audio:')
                       [0] + 1][0].strip()
    if show_metacritic_score == '':
        show_metacritic_score = np.NAN
    else:
        show_metacritic_score = int(show_metacritic_score[:-4])
    if len(show_IMDb_score) < 3:
        show_IMDb_score = np.NAN
    else:
        show_IMDb_score = float(show_IMDb_score[:-3])
    if len(show_age_restriction.strip()) < 2 or \
            show_age_restriction[-1] != '+':
        show_age_restriction = np.NAN
    else:
        show_age_restriction = int(show_age_restriction[:-1])
    df.loc[-1] = [show_name, show_type, show_description,
                  show_genre, show_alt_genre,
                  show_streaming_countries,
                  show_IMDb_score, show_metacritic_score,
                  show_age_restriction,
                  show_family_friendly, show_year, show_audio]
    df.index = df.index + 1


# For every country, go through every show and parse it and then add it to a
# hashtable, if the file is already in the hashtable then we skip over and go
# to the next show. Once you are done with all shows, you move to the next show
def scrape_website():
    for country in country_list:
        for page_num in range(1, max_page_num + 1):
            try:
                if verbose:
                    print(datetime.now().strftime('[%d/%m/%Y %H:%M:%S]: ')
                          + 'Now working on page {} of country {}'.format(
                                                         page_num, country))
                print(datetime.now().strftime('[%d/%m/%Y %H:%M:%S]: ') +
                      'Now working on page {} of country {}'.format(
                                    page_num, country), file=log_file)
                url = 'https://www.flixwatch.co/catalogue/netflix-{}/?' \
                      'paged={}'.format(country.lower().replace(' ', '-'),
                                        page_num)
                res = requests.get(url)
                html_page = res.content
                soup = BeautifulSoup(html_page, 'html.parser')
                for link in soup.find_all('a', href=True):
                    curr_show = link['href']
                    if hash(curr_show) not in shows_hash_table and \
                            (('movies' in curr_show) or (
                                    'tvshows' in curr_show)):
                        shows_hash_table[hash(curr_show)] = curr_show
                        show_res = requests.get(curr_show)
                        show_html_page = show_res.content
                        show_soup = BeautifulSoup(show_html_page,
                                                  'html.parser')
                        show_text = show_soup.find_all(text=True)
                        show_array = np.array([])
                        for line in show_text:
                            if line.parent.name in ['b', 'p', 'span', 'a',
                                                    'h1']:
                                show_array = np.append(show_array, line)
                        if 'movies' in curr_show:
                            parse_show_page(show_array, show_type='movie')
                        else:
                            parse_show_page(show_array, show_type='tvshow')

            except Exception as e:
                if verbose:
                    print(datetime.strftime('[%d/%m/%Y %H:%M:%S]: ',
                                            datetime.now())
                          + 'Failed while creating show link table at country '
                            '= {} and page_num = {} due to exception {}'
                          .format(country, page_num, e))
                print(datetime.strftime('[%d/%m/%Y %H:%M:%S]: ',
                                        datetime.now())
                      + 'Failed while creating show link table at country '
                        '= {} and page_num = {} due to exception {}'
                      .format(country, page_num, e),
                      file=log_file)
                log_file.close()
                traceback.print_exc(file=log_file)
                traceback.print_exc()
                sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='main.py [-h] [-v] [-l LogFile.txt]'
                                           ' [-o Output.csv]',
                                     description='Scrape www.flixwatch.co'
                                                 'website and create a csv '
                                                 'file with the data.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Setting '
                        'the Verbose option enables printing the log files to '
                        'the screen in real time')
    parser.add_argument('-l', '--log', required=False, default='log.txt',
                        help='Pass the name of the log file you want to create'
                             '. The name must end in .txt the default is '
                             'log.txt ')
    parser.add_argument('-o', '--out', required=False, default='dataset.csv',
                        help='Pass the name of the csv file you want to create'
                             '. The name must end in .csv the default is '
                             'dataset.csv')
    io_args = parser.parse_args()
    verbose = io_args.verbose
    log_path = io_args.log
    output_path = io_args.out
    try:
        if not log_path.endswith('.txt'):
            raise IOError
        log_file = open(log_path, 'w', encoding='utf-8')
    except IOError:
        if verbose:
            print('Was not able to create the log file')
            traceback.print_exc()
        sys.exit(0)
    try:
        if not output_path.endswith('.csv'):
            raise IOError
        elif os.path.isfile(output_path):
            csv_file = open(output_path, 'w')
            csv_file.close()
    except IOError:
        if verbose:
            print('Was not able to create the csv file')
            traceback.print_exc()
            sys.exit(0)
    max_page_num = int(get_max_page_num())
    country_list = get_list_of_countries()
    shows_hash_table = {}
    df = pd.DataFrame(
        columns=('Name', 'Type', 'Description', 'Genre', 'AltGenre',
                 'StreamingCountries', 'IMDbScore',
                 'MetacriticScore', 'Age', 'FamilyFriendly', 'Year',
                 'Audio'))
    scrape_website()
    df = df.sort_index()
    df.to_csv(output_path, index=False)
    if verbose:
        print(datetime.now().strftime('[%d/%m/%Y %H:%M:%S]: ')
              + 'File {} was created.'.format(output_path))
    print(datetime.now().strftime('[%d/%m/%Y %H:%M:%S]: ')
          + 'File {} was created.'
          .format(output_path), file=log_file)
    log_file.close()
    sys.exit(1)
