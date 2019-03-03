import matplotlib.pyplot as plt
import bs4
import requests
import sys

bs = bs4.BeautifulSoup

def create_url(year):
    url_base = "https://www.inflation.eu/inflation-rates/"
    year = str(year)
    return url_base + f"cpi-inflation-{year}" + ".aspx"


def pull_data(countries, y):
    countries_this_year = [pull_name(country[1]) for country in countries]
    rates_this_year = [pull_rate(country[-2]) for country in countries]
    return countries_this_year, rates_this_year

def pull_name(td):
    return td.text[15:-5]
    
def pull_rate(td):

    ## unfortunate special case. Some rates may be missing. If the rate is not of form d.dd#, where d is digit and # is special character, we will return 0.00
    try:
        rate = td.text[:-3]
        rate_parts = rate.split(".")
        if len(rate_parts) == 2:
            return float(rate)
        else:
            rate = float(str(rate_parts[0]) + str(rate_parts[1]) + "." + str(rate_parts[-1]))
            return rate
    except IndexError:
        return 0.00

def compile_(d, c, r, y):
    number_of_countries = len(c)
    index = 0
    while index < number_of_countries:
        if c[index] in d:
            d[c[index]][y] = r[index]
        else:
            d[c[index]] = dict({y: r[index]})
        index += 1

if __name__ == "__main__":

    if len(sys.argv) == 1:
        start_year = 1973
        end_year = 2018 ## modify as needed. Leave as current year - 1.
    else:
        start_year = int(sys.argv[1])
        end_year = 2018

    url_list = dict({})

    for year in range(start_year, end_year + 1):
        url_list[year] = create_url(year)

    data = dict({})

    for year in range(start_year, end_year + 1):
        source = requests.get(url_list[year])
        sauce = source.text
        source.close()
        
        soup = bs(sauce, "html5")
        countries_this_year = []
        rates_this_year = []
        
        odd_countries = soup.find_all(class_ = "tabledata1")
        even_countries = soup.find_all(class_ = "tabledata2")
        countries = odd_countries + even_countries
        countries = [country.contents for country in countries]
        
        countries_this_year, rates_this_year = pull_data(countries, year)
        
        compile_(data, countries_this_year, rates_this_year, year)
        print(f"Completed scraping data for {year}.")


    import pickle

    with open(f'inflation_data_{start_year}_{end_year}.pickle', 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    