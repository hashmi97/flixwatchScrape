import requests
from bs4 import BeautifulSoup
import os
import traceback
import pandas as pd
import sys
import numpy as np


def get_list_of_countries():
    country_url = "https://www.flixwatch.co/catalogs/"
    country_res = requests.get(country_url)
    country_html_page = country_res.content
    country_soup = BeautifulSoup(country_html_page, 'html.parser')
    countries = np.array([])
    for web_line in country_soup.find_all(text=True):
        if web_line.parent.name in ["a", "details"]:
            countries = np.append(countries, (web_line.parent.name, web_line))
    countries = countries[np.min(np.where(countries == "details")):
                          np.max(np.where(countries == "details"))]
    countries = countries[np.logical_and(
        countries != "details", np.logical_and(countries != "a", countries !=
                                               "\n"))]
    countries = np.append(countries, 'Mongolia')
    countries.sort()
    return countries


def get_max_page_num():
    global max_page_num, line
    page_num_url = "https://www.flixwatch.co/catalogue/netflix-usa"
    page_num_res = requests.get(page_num_url)
    page_num_html_page = page_num_res.content
    page_num_soup = BeautifulSoup(page_num_html_page, 'html.parser')
    max_page_num = 0
    for line in page_num_soup.find_all(text=True):
        if line.parent.name == 'a':
            if "Next" in line:
                break
            max_page_num = line
    return max_page_num


def parse_show_page(array, show_type):
    global df, log_file
    array = array[11:-5]
    show_name = array[0]
    print('Now working on show {}'.format(show_name), file=std_orig)
    print('Now working on show {}'.format(show_name))
    show_description = array[2]
    show_genre = "".join(
        array[np.where(array == "Genre:")[0] + 1]).strip()
    show_alt_genre = "".join(array[np.where(
        array == "Alternate Genre:")[0] + 1]).strip()
    show_streaming_countries = ''
    i = np.where(array == "Streaming in:")[0] + 1
    while array[i] != "IMDb:":
        show_streaming_countries = (show_streaming_countries +
                                    str(array[i][0])).strip()
        i += 1
    show_IMDb_score = array[
        np.where(array == "IMDb:")[0] + 1][0].strip()
    show_metacritic_score = array[np.where(
        array == "Metacritic:")[0] + 1][0].strip()
    show_age_restriction = array[
        np.where(array == "Suitable for Age ")[0] + 3][0]
    show_family_friendly = array[
        np.where(array == "Family Friendly:")[0] + 1][0].strip()
    show_year = int(
        array[np.where(array == "Year:")[0] + 1])
    show_audio = array[np.where(array == "Audio:")
                       [0] + 1][0].strip()
    if show_metacritic_score == "":
        show_metacritic_score = np.NAN
    else:
        show_metacritic_score = int(show_metacritic_score[:-4])
    if len(show_IMDb_score) < 3:
        show_IMDb_score = np.NAN
    else:
        show_IMDb_score = float(show_IMDb_score[:-3])
    if len(show_age_restriction.strip()) < 2 or \
            show_age_restriction[-1] != "+":
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


if __name__ == '__main__':
    verbose = True
    output_path = os.path.join("files", "data.csv")
    log_file = open(os.path.join("files", "log.txt"), "w", encoding="utf-8")
    max_page_num = int(get_max_page_num())
    country_list = get_list_of_countries()
    shows_hash_table = {}
    std_orig = sys.stdout
    sys.stdout = log_file

    df = pd.DataFrame(
        columns=('Name', 'Type', 'Description', 'Genre', 'AltGenre',
                 'StreamingCountries', 'IMDbScore',
                 'MetacriticScore', 'Age', 'FamilyFriendly', 'Year',
                 'Audio'))

    for country in country_list:
        for page_num in range(1, max_page_num + 1):
            try:
                print("Now working on page: {} of country: {}".format(page_num,
                                                                      country))
                print("Now working on page: {} of country: {}".format(page_num,
                                                                      country),
                      file=std_orig)
                url = "https://www.flixwatch.co/catalogue/netflix-{}/?" \
                      "paged={}".format(country.lower().replace(" ", "-"),
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
                            parse_show_page(show_array, show_type="movie")
                        else:
                            parse_show_page(show_array, show_type="tvshow")

            except Exception as e:
                print(
                    'Failed while creating show link table at country = {} and'
                    ' page_num = {} due to exception {}'.format(country,
                                                                page_num, e))
                print(
                    'Failed while creating show link table at country = {} and'
                    ' page_num = {} due to exception {}'.format(country,
                                                                page_num, e),
                    file=std_orig)
                log_file.close()
                if verbose:
                    traceback.print_exc(file=std_orig)
                    traceback.print_exc()

    df = df.sort_index()
    sys.stdout = std_orig
    log_file.close()
    df.to_csv(output_path, index=False)
