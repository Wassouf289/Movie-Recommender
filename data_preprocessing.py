import pandas as pd 
from sqlalchemy import create_engine
import re


def get_year_from_title (title):
    '''Extract year from title'''
    year = re.findall((r"\((\d{4})\)$"),title)
    return year

# read data from csv files 
ratings = pd.read_csv('ml-latest-small/ratings.csv')
movies = pd.read_csv('ml-latest-small/movies.csv')

movies_ratings = pd.merge(ratings,movies, how='outer', left_on='movieId', right_on='movieId')
# add the year column
movies_ratings['year'] = movies_ratings['title'].apply(get_year_from_title)
# remove year from title
movies_ratings['title'] = movies_ratings['title'].str.replace(r"\((\d{4})\)$", "")
movies_ratings['title'] = movies_ratings['title'].str.strip()
#Remove movies which have been rated
movies_ratings.dropna(subset=['userId'], how='any',inplace=True)

# store in postqres
HOST = 'localhost'
PORT = '5432'
DBNAME = 'movies_db'
connection_string = f'postgres://{HOST}:{PORT}/{DBNAME}'
db = create_engine(connection_string)
movies_ratings.to_sql('movies_ratings', db)


