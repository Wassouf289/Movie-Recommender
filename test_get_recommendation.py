import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from helper_functions import movieTitle_to_id
from NMF_recommend import recommend_NMF
from userBased_filtering_recommend import user_based_filtering_recommend
from recommend_movies import Movie_Recommender

movies_num = 5

#create connection to movies db
HOST = 'localhost'
PORT = '5432'
DBNAME = 'movies_db'
connection_string = f'postgresql://{HOST}:{PORT}/{DBNAME}'
db = create_engine(connection_string)

user_movies = ['Titanic','Afterglow','Forgetting Sarah Marshall','Bella','Heat']
user_ratings = ['5.0','5.0','4.0','4.0','5.0']

Movie_Recommender = Movie_Recommender(user_movies,user_ratings)
movies_ratings= Movie_Recommender.get_movies_ratings_data()
user_movies_ids = movieTitle_to_id(user_movies,movies_ratings)
new_user_vector = Movie_Recommender.new_user(user_movies_ids,user_ratings,movies_ratings)
recommended_movies = recommend_NMF(new_user_vector,movies_num,movies_ratings)

def test_getting_movies_ids():
    assert type(user_movies_ids) == list
    assert isinstance(user_movies_ids[0],int)
    assert len(user_movies_ids) == 5



def test_get_recommendation():
    assert isinstance(recommended_movies,list)
    assert isinstance(recommended_movies[0],str)
    assert len(recommended_movies) == movies_num 



def test_recommended_movies():
    ''' test if the recommended movies are valid ones from DB'''

    for movie in recommended_movies:
        movie_id = f"SELECT 'movieId' FROM movies_ratings WHERE title ='{movie}';"
        assert movie_id != None
