from flask import Flask,render_template,request
from recommend_movies import Movie_Recommender
from NMF_recommend import recommend_NMF
from userBased_filtering_recommend import user_based_filtering_recommend
from helper_functions import movieTitle_to_id
from sqlalchemy import create_engine

app = Flask(__name__)


@app.route('/')
def main_page():
    return render_template('main_page.html')

@app.route('/recommender')
def recommend():
    return render_template('recommendation.html')

@app.route('/recommended-movies')
def get_recommendation():
    #number of movies to recommend
    movies_num = 5
    #number of neighbours (similar users)
    n_neighbor = 3
    
    #create connection to movies db
    HOST = 'localhost'
    PORT = '5432'
    DBNAME = 'movies_db'
    connection = f'postgresql://{HOST}:{PORT}/{DBNAME}'
    db = create_engine(connection)

    user_movies_ratings = request.args
    user_movies_ratings_dict = dict(user_movies_ratings).values()
    # get a list of user input movies and ratings
    user_movies_ratings_list = list(user_movies_ratings_dict)
    # get user movies : get every second element from the list
    user_movies = user_movies_ratings_list[::2]
    user_movies = user_movies[:-1]
    user_movies_fuzzed = []
    for movie in user_movies:
        # Search for the name of the movie in the database using tsvector
        movie_name_query = f"""SELECT title,
                        ts_rank_cd(to_tsvector('english', movies_ratings.title), to_tsquery('''{movie}'':*'))
                        AS score
                        FROM movies_ratings
                        WHERE to_tsvector('english', movies_ratings.title) @@ to_tsquery('''{movie}'':*')
                        ORDER BY score DESC;"""
        result = db.execute(movie_name_query).fetchall()[0][0]
        user_movies_fuzzed.append(result)
    
    print(user_movies_fuzzed)

    # get user ratings for the movies: using list slicing
    user_ratings = user_movies_ratings_list[1::2]
    print(user_ratings)
    movie_recommender = Movie_Recommender(user_movies_fuzzed,user_ratings)
    movies_ratings= movie_recommender.get_movies_ratings_data()
    user_movies_ids = movieTitle_to_id(user_movies_fuzzed,movies_ratings)
    new_user_vector = movie_recommender.new_user(user_movies_ids,user_ratings,movies_ratings)
    recommended_movies = recommend_NMF(new_user_vector,movies_num,movies_ratings)
    #recommended_movies = user_based_filtering_recommend(new_user_vector,user_movies_ids,movies_num,n_neighbor,movies_ratings)


    return render_template('recommended_movies.html',movies=recommended_movies)    


if __name__ == "__main__":
    app.run(debug=True, port=5000)
    