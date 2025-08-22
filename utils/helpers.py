import pandas as pd
import numpy as np
import joblib
from config.paths_config import *

# 1. Get anime frame
def getAnimeFrame (anime, path_df):
    df = pd.read_csv(path_df)
    if isinstance(anime, int):
        return df[df.anime_id == anime]
    if isinstance(anime, str):
        return df[df.eng_version == anime]

# 2. Get synopsis
def getSynopsis(anime, synopsis_path):
    df = pd.read_csv(synopsis_path)
    if isinstance(anime, int):
        row = df[df.MAL_ID == anime]
    elif isinstance(anime, str):
        row = df[df.Name == anime]
    else:
        return "Invalid anime identifier"
    if row.empty:
        return "No synopsis available"
    return row['sypnopsis'].values[0]

# 3. Find similar animes
def find_similar_animes(name, path_anime_weights, path_anime_encoding, path_anime_decoding, path_anime_df, path_synopsis_df, 
                        n=10, return_dist=False, neg=False):
    anime_weights = joblib.load(path_anime_weights)
    anime_encoding = joblib.load(path_anime_encoding)
    anime_decoding = joblib.load(path_anime_decoding)
    # synopsis_df = pd.read_csv(path_synopsis_df)
    try:
        index = getAnimeFrame(name,path_anime_df).anime_id.values[0]
        encoded_index = anime_encoding.get(index)

        if encoded_index is None:
            raise ValueError(f"Encoded index not found for anime ID: {index}")
        
        weights = anime_weights
        dists = np.dot(weights,weights[encoded_index])
        sorted_dists = np.argsort(dists)
        n = n + 1
        if neg:
            closest = sorted_dists[:n]
        else:
            closest = sorted_dists[-n:]

        if return_dist:
            return dists, closest
        
        SimilarityArr = []
        for x in closest:
            decoded_id = anime_decoding.get(x)
            synopsis = getSynopsis(decoded_id, path_synopsis_df)
            anime_frame = getAnimeFrame(decoded_id, path_anime_df)
            anime_name = anime_frame.eng_version.values[0]
            genre = anime_frame.Genres.values[0]
            similarity = dists[x]

            SimilarityArr.append({
                "anime_id" : decoded_id,
                "name" : anime_name,
                "similarity" : similarity,
                "genre" : genre,
                "synopsis" : synopsis
            })
        
        Frame = pd.DataFrame(SimilarityArr).sort_values(by="similarity", ascending=False)
        Frame = Frame[Frame.anime_id != index]
        return Frame.drop(["anime_id"],axis=1)

    except:
        print("error occured")

# 4. Find similar users
def find_similar_users(input, path_user_weights, path_user_encoding, path_user_decoding, n=10, return_dist=False, neg=False):
    user_weights = joblib.load(path_user_weights)
    user_encoding = joblib.load(path_user_encoding)
    user_decoding = joblib.load(path_user_decoding)
    try:
        index = input
        encoded_index = user_encoding.get(index)

        weights = user_weights
        dists = np.dot(weights, weights[encoded_index])
        sorted_dists = np.argsort(dists)
        n = n + 1

        if neg:
            closest = sorted_dists[:n]
        else:
            closest = sorted_dists[-n:]

        if return_dist:
            return dists, closest
        
        SimilarityArr = []

        for x in closest:
            similarity = dists[x]
            if isinstance(input, int):
                decoded_id = user_decoding.get(x)
                SimilarityArr.append({
                    "similar_users": decoded_id,
                    "similarity": similarity
                })
        similar_users = pd.DataFrame(SimilarityArr).sort_values(by="similarity", ascending=False)
        similar_users = similar_users[similar_users.similar_users != input]
        return similar_users
    
    except Exception as e:
        print("Error occured", e)
        
# 5. Get user preferences
def get_user_preferences(user_id, path_rating_df, path_anime_df, verbose=0):
    rating_df = pd.read_csv(path_rating_df)
    df = pd.read_csv(path_anime_df)

    animes_watched_by_user = rating_df[rating_df.user_id == user_id]
    user_rating_precentile = np.percentile(animes_watched_by_user.rating, 75)
    animes_watched_by_user = animes_watched_by_user[animes_watched_by_user.rating >= user_rating_precentile]
    top_animes_user = (
        animes_watched_by_user.sort_values(by="rating", ascending=False).anime_id.values
    )
    anime_df_rows = df[df["anime_id"].isin(top_animes_user)]
    anime_df_rows = anime_df_rows[["eng_version", "Genres"]]

    return anime_df_rows

# 6. Get user recomendations
def get_user_recomendations(similar_users, user_preferences, path_anime_df, path_synopsis_df, path_rating_df, n=10):
    recommndations = []
    anime_list = []

    for user_id in similar_users.similar_users.values:
        pref_list = get_user_preferences(int(user_id), path_rating_df, path_anime_df)
        pref_list = pref_list[pref_list.eng_version.isin(user_preferences.eng_version.values)]

        if not pref_list.empty:
            anime_list.append(pref_list.eng_version.values)
    
    if anime_list:
        anime_list = pd.DataFrame(anime_list)
        sorted_list = pd.DataFrame(pd.Series(anime_list.values.ravel()).value_counts()).head(n)

        for i, anime_name in enumerate(sorted_list.index):
            n_user_pref = sorted_list[sorted_list.index == anime_name].values[0][0]
            if isinstance(anime_name, str):
                frame = getAnimeFrame(anime_name, path_anime_df)
                anime_id = frame.anime_id.values[0]
                genre = frame.Genres.values[0]
                synopsis = getSynopsis(int(anime_id), path_synopsis_df)

                recommndations.append({
                    "n" : n_user_pref,
                    "anime_name": anime_name,
                    "Genre" : genre,
                    "Synopsis" : synopsis
                })
    
    return pd.DataFrame(recommndations).head(n)