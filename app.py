import streamlit as st
import pickle
import pandas as pd
import requests

# ---------------------- Load Data ----------------------
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

TMDB_API_KEY = "46660c76c7ff58983b9f1d0bc425350e"  # Your API Key


# ---------------------- TMDB API Functions ----------------------
def get_movie_id(movie_title):
    """Fetch movie ID from TMDB using the title"""
    url = f"https://api.themoviedb.org/3/search/movie?query={movie_title}&api_key={TMDB_API_KEY}"
    response = requests.get(url).json()

    if response and 'results' in response and len(response['results']) > 0:
        return response['results'][0]['id']
    return None


def fetch_movie_details(movie_id):
    """Fetch detailed movie information from TMDB"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    response = requests.get(url).json()

    if response:
        return {
            "title": response.get("title", "N/A"),
            "overview": response.get("overview", "No description available."),
            "poster": f"https://image.tmdb.org/t/p/w500{response['poster_path']}" if response.get(
                "poster_path") else "https://via.placeholder.com/300x450?text=No+Image",
            "release_date": response.get("release_date", "N/A"),
            "rating": response.get("vote_average", "N/A"),
            "genres": ", ".join([genre["name"] for genre in response.get("genres", [])]),
        }
    return None


# ---------------------- Recommendation Function ----------------------
def recommend(movie):
    """Get top 5 recommended movies with details"""
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]

        movie_indices = sorted(enumerate(distances), key=lambda x: x[1], reverse=True)[1:6]
        recommended_movies = [movies.iloc[i[0]]['title'] for i in movie_indices]

        movie_details = [fetch_movie_details(get_movie_id(title)) for title in recommended_movies]

        return movie_details
    except Exception as e:
        st.error(f"❌ Error in Recommendation: {e}")
        return []


# ---------------------- Streamlit UI ----------------------
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

st.markdown(
    """
    <style>
    /* Full Dark Cinematic Background */
    body {
        background: #000;
        color: white;
        font-family: 'Poppins', sans-serif;
    }

    /* Neon Gradient Background */
    .main {
        background: linear-gradient(120deg, #000000, #121212, #1a1a1a);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 0px 15px rgba(255, 0, 150, 0.3);
    }

    /* Title with Glow Effect */
    .title {
        font-size: 36px;
        text-align: center;
        font-weight: bold;
        color: #ff0099;
        text-shadow: 0px 0px 10px rgba(255, 0, 150, 0.7);
    }

    /* Selectbox Styling */
    .stSelectbox label {
        color: white;
        font-size: 16px;
    }

    /* Movie Card */
    .movie-card {
        background: linear-gradient(145deg, #1a1a1a, #121212);
        padding: 14px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0px 5px 15px rgba(255, 0, 150, 0.4);
        transition: transform 0.3s ease-in-out, box-shadow 0.3s;
    }
    .movie-card:hover {
        transform: scale(1.05);
        box-shadow: 0px 10px 20px rgba(255, 0, 150, 0.6);
    }

    /* Movie Image */
    .movie-card img {
        border-radius: 12px;
        width: 100%;
        transition: opacity 0.4s ease-in-out;
    }
    .movie-card:hover img {
        opacity: 0.8;
    }

    /* Movie Details */
    .movie-title {
        font-weight: bold;
        font-size: 18px;
        margin: 12px 0;
        color: #ff0099;
    }
    .movie-details {
        font-size: 14px;
        opacity: 0.8;
        color: #bbb;
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(45deg, #ff0099, #ff6600);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #ff6600, #ff0099);
        transform: scale(1.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------- UI Elements ----------------------
st.markdown('<div class="title">🔥 Movie Recommender System</div>', unsafe_allow_html=True)

selected_movie_name = st.selectbox("🔍 Select a movie:", movies['title'].values)

if st.button("🎬 Get Recommendations"):
    st.subheader("💡 Recommended Movies:")

    recommended_movies = recommend(selected_movie_name)

    # ✅ Display movies in a grid layout
    cols = st.columns(5)  # Five columns for five movies

    for idx, movie in enumerate(recommended_movies):
        if movie:
            with cols[idx]:  # ✅ Assign each movie to a column
                st.markdown(
                    f"""
                    <div class="movie-card">
                        <img src="{movie['poster']}" alt="{movie['title']} Poster" style="width:100%;">
                        <div class="movie-title">{movie['title']}</div>
                        <div class="movie-details">
                            ⭐ {movie['rating']} | 📅 {movie['release_date']} <br>
                            🎭 {movie['genres']} <br>
                            {movie['overview'][:80]}...
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
