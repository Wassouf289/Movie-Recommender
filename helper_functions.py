
def movieId_to_title(movies_ids_list,movies):
    """ Convert a list of movie ids to a list of movie titles """
    movies_list = []
    for i in movies_ids_list:

        name = list(movies['title'][movies['movieId'] == i])[0]
        movies_list.append(name)
    return movies_list

def movieTitle_to_id(movies_titles_list,movies):
    """
    Convert a list of movie titles to a list of movie ids
    """
    movies_list = []
    for i in movies_titles_list:
        id = list(movies['movieId'][movies['title'] == i])[0]
        movies_list.append(id)
    return movies_list