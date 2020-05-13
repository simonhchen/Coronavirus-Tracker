# Collects daily COVID-19 cases from John Hopkins Repo

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import pandas as pd

base = "https://raw.githubusercontent.com"
url = requests.get(
    'https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports').text
soup = BeautifulSoup(url, features="html.parser")

# Collects all daily CSVs from John Hopkins github and saves them within data dictionary
data_dict = {}

for link in (urljoin(base, a["href"]) for a in soup.select("a[href$='.csv']")):
    link = link.replace('/blob', '')
    #  Stores each daily COVID-19 .csv file in John Hopkins repo as a dataframe in a dictionary
    data_dict[link.replace(
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/",
        "").replace(".csv", "")] = pd.read_csv(link)


# prints out all dataframes within the dictionary
for value in data_dict.values():
    print(value)


