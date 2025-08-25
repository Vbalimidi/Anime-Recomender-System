# from config.paths_config import *
# from utils.helpers import *


# def hybrid_recommendation(user_id , user_weight=0.5, content_weight =0.5):

#     ## User Recommndation

#     similar_users =find_similar_users(user_id,USER_WEIGHTS_PATH,USER_ENCODING,USER_DECODING)
#     user_pref = get_user_preferences(user_id , RATING_DF, DF)
#     user_recommended_animes =get_user_recomendations(similar_users, user_pref, DF, SYNOPSIS_DF, RATING_DF)
    

#     user_recommended_anime_list = user_recommended_animes["anime_name"].tolist()

#     #### Content recommendation
#     content_recommended_animes = []

#     for anime in user_recommended_anime_list:
#         similar_animes = find_similar_animes(anime, ANIME_WEIGHTS_PATH, ANIME_ENCODING, ANIME_DECODING, DF, SYNOPSIS_DF)

#         if similar_animes is not None and not similar_animes.empty:
#             content_recommended_animes.extend(similar_animes["name"].tolist())
#         else:
#             print(f"No similar anime found {anime}")
    
#     combined_scores = {}

#     for anime in user_recommended_anime_list:
#         combined_scores[anime] = combined_scores.get(anime,0) + user_weight

#     for anime in content_recommended_animes:
#         combined_scores[anime] = combined_scores.get(anime,0) + content_weight  

#     sorted_animes = sorted(combined_scores.items() , key=lambda x:x[1] , reverse=True)

#     return [anime for anime , score in sorted_animes[:10]] 


from config.paths_config import *
from utils.helpers import *

def anime_recommendation(anime_name, n=10):
    """
    Recommends similar animes based on a given anime name using content-based filtering.

    Args:
        anime_name (str): The name of the anime to find recommendations for.
        n (int): The number of recommendations to return.

    Returns:
        list: A list of anime names that are similar to the input anime.
    """
    similar_animes_df = find_similar_animes(
        anime_name,
        ANIME_WEIGHTS_PATH,
        ANIME_ENCODING,
        ANIME_DECODING,
        DF,
        SYNOPSIS_DF,
        n=n
    )

    if similar_animes_df is not None and not similar_animes_df.empty:
        return similar_animes_df["name"].tolist()
    else:
        print(f"No similar anime found for {anime_name}")
        return []