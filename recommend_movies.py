import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from helper_functions import movieTitle_to_id
from NMF_recommend import recommend_NMF
from userBased_filtering_recommend import user_based_filtering_recommend



class Movie_Recommender:

    def __init__(self,user_movies,user_ratings):
        """ init with user movies list and user ratings for those movies"""
        self.user_movies = user_movies
        self.user_ratings = user_ratings


    def get_movies_ratings_data(self):
        """ get movies ratings data stored in postqres"""
        HOST = 'localhost'
        PORT = '5432'
        DBNAME = 'movies_db'
        connection_string = f'postgresql://{HOST}:{PORT}/{DBNAME}'
        db = create_engine(connection_string)
        movies_ratings = pd.read_sql_query("SELECT * FROM movies_ratings;", db)
        return movies_ratings



    def new_user(self,user_movies_ids,user_ratings,movies_ratings):
        """ This function takes users input movies and ratings and create a new user rating vector"""
        movies_list_ids = movies_ratings['movieId'].unique()
        empty_list = [np.nan] * len(movies_list_ids)
        rating_dict = dict(zip(movies_list_ids,empty_list))
        for movie,rating in zip(user_movies_ids,user_ratings):
            rating_dict[movie]= float(rating)
        new_user_vector = list(rating_dict.values())
        return new_user_vector

    

  
if __name__ == '__main__':

    #number of movies to recommend
    movies_num = 5
    #number of neighbours (similar users)
    n_neighbor = 3

    user_movies = ['Titanic','Afterglow','Forgetting Sarah Marshall','Bella','Heat']
    user_ratings = ['5.0','5.0','4.0','4.0','5.0']
    Movie_Recommender = Movie_Recommender(user_movies,user_ratings)
    movies_ratings= Movie_Recommender.get_movies_ratings_data()
    user_movies_ids = movieTitle_to_id(user_movies,movies_ratings)
    new_user_vector = Movie_Recommender.new_user(user_movies_ids,user_ratings,movies_ratings)
    recommended_movies = recommend_NMF(new_user_vector,movies_num,movies_ratings)
    print(recommended_movies)
    recommended_movies = user_based_filtering_recommend(new_user_vector,user_movies_ids,movies_num,3,movies_ratings)
    print(recommended_movies)
