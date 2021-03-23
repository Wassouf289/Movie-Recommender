
import pandas as pd
import numpy as np
import pickle
from sqlalchemy import create_engine
from sklearn.decomposition import NMF
from helper_functions import movieId_to_title


def train_nmf(movies_ratings):
    """ train nmf model and save to disk """
    
    #pivot the dataframe
    movies_ratings = movies_ratings.pivot_table(index='userId', columns='movieId', values='rating')
    #Fill Nan with 3.0 rating:
    movies_ratings.fillna(3.0, inplace=True)

    nmf_model = NMF(
        n_components=20,
        init='random',
        random_state=10,
        max_iter=10000
    )
    nmf_model.fit(movies_ratings)

    #save nmf model
    pickle.dump(nmf_model,open("models/nmf_model.sav", 'wb'))


def load_NMF_model():
    """
    Load NMF model, return the model and movie weights
    """
    model = pickle.load(open("models/nmf_model.sav", 'rb'))
    Q = model.components_  
    return model, Q

def recommend_NMF(new_user,movies_num,movies_ratings):
    """ This function takes the rating vector from new user and recommend
        movies_num of movies for the user based on NMF
    """
    list_id_movies = movies_ratings['movieId'].unique()
    nmf,Q = load_NMF_model()
    new_user_vector = pd.DataFrame(new_user, index=list_id_movies).T
    new_user_vector_filled = new_user_vector.fillna(3)
    #calculate Matrix P (Genres)
    P = nmf.transform(new_user_vector_filled)
    #make predictions
    predictions = np.dot(P,Q)
    recommendations = pd.DataFrame(predictions.reshape(-1), index=list_id_movies).T
    #Remove already watched movies:
    not_watched_movies_mask = np.isnan(new_user_vector)
    not_watched = recommendations[not_watched_movies_mask]

    top_movies_ids = not_watched.T.sort_values(by=[0], ascending=False).index[:movies_num]

    Top_recommended = movieId_to_title(top_movies_ids,movies_ratings) 
    return Top_recommended


if __name__ == '__main__':

    #create connection to movies db
    HOST = 'localhost'
    PORT = '5432'
    DBNAME = 'movies_db'
    connection_string = f'postgresql://{HOST}:{PORT}/{DBNAME}'
    db = create_engine(connection_string)
    movies_ratings = pd.read_sql_query("SELECT * FROM movies_ratings;", db)
    
    #train NMF
    train_nmf(movies_ratings)

