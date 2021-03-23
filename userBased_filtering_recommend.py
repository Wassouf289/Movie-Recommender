import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sklearn.utils
from helper_functions import movieId_to_title


def user_based_filtering_recommend(new_user,user_movies_ids,movies_num,n_neighbor,movies_ratings):
    """ This function return number of recommended movies based on user based filtering using 
    cosine similarity to find the most similar users to the new user 
    it returns movies_num of movies from the top ranked movies of n_neighbour users 
    who are the most similar to the new user"""
    #pivot the dataframe
    users_inDB = movies_ratings.pivot_table(index='userId', columns='movieId', values='rating')

    list_id_movies = movies_ratings['movieId'].unique()
    
    new_user_vector = pd.DataFrame(new_user, index=list_id_movies).T

    #fill Nans with 3 rating
    users_inDB = users_inDB.fillna(3.0)
    new_user_vector_filled = new_user_vector.fillna(3.0)

    #for cosine similarity we have to center the data in order to have a magnitude(0-1)
    users_inDB = (users_inDB - 3.0)/2.0
    new_user = (new_user_vector_filled - 3.0)/2.0

    #label the new user that we want to recommend for:
    new_user.index=['new_user']

    #add the new use to the original df 
    users_matrix = pd.concat([users_inDB,new_user])
    #calculate cosine similarity
    users_similarity_matrix = cosine_similarity(users_matrix)
    users_similarity_matrix = pd.DataFrame(users_similarity_matrix,index=users_matrix.index,columns=users_matrix.index)
    #we get here (users_num*users_num) similarity matrix
    #print(users_matrix_similarity)

    # get the new user similarities row: except the last column value(similarity with himself=1)
    new_user_similarity = users_similarity_matrix['new_user'].iloc[:-1]
    # take the n_neighbors nearest users (N users who have the most similarity with the new user)
    similar_users = new_user_similarity.nlargest(n_neighbor).index.values
    #print(similar_users)

    #we will get (movies_num*n_neighbor*2) movies to choose
    recommended_movieIds = []
    scores = []
    for user in similar_users:
        recommended_movieIds.extend(users_inDB.loc[user].nlargest(movies_num*2).index)
        scores.extend(users_inDB.loc[user].nlargest(movies_num*2).values)
    
    recommended_movies_dic = {'movie_id':recommended_movieIds,'score':scores}
    recommended_movies_df = pd.DataFrame(recommended_movies_dic)
    #print(recommended_movies_df)

    #Shuffle the movies
    recommended_movies_df = sklearn.utils.shuffle(recommended_movies_df)
    #Order movies by score
    recommended_movies_df = recommended_movies_df.sort_values(by='score',ascending=False)
    recommended_movies_ids = recommended_movies_df['movie_id'].unique()

    #get the final recommendation: retrn movies_num of movies which the user hasn't rated
    top_recommended_movies = []
    for movie_id in recommended_movies_ids:
        if (movie_id not in user_movies_ids) and (len(top_recommended_movies) < movies_num) :
            top_recommended_movies.append(movie_id)

    #finally return the movies titles 
    top_recommended_movies = movieId_to_title(top_recommended_movies,movies_ratings)
    return top_recommended_movies



