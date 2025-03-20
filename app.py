import streamlit as st
import pickle
import pandas as pd
import requests
import gdown
import os
import concurrent.futures

# ---------------------- Streamlit Page Config ----------------------
st.set_page_config(page_title="🎬 Movie Recommender", page_icon="🍿", layout="wide")

# ---------------------- Download Data from Google Drive ----------------------
def download_file(url, output):
    """Download file from Google Drive if it doesn't exist"""
    if not os.path.exists(output):
        with st.spinner(f"📥 Downloading {output}..."):
            gdown.download(url, output, fuzzy=True, quiet=False)

# Google Drive links for PKL files
MOVIE_DICT_URL = "https://drive.google.com/uc?id=1_k6bbRDRDwqocVRaoWARQToq3OIbynl6"
SIMILARITY_URL = "https://drive.google.com/uc?id=1QqvIlbT3F3PD9I277DqM6CKCDkzo-_Rn"

# Filenames
MOVIE_DICT_FILE = "movie_dict.pkl"
SIMILARITY_FILE = "similarity.pkl"

# Download files if missing
download_file(MOVIE_DICT_URL, MOVIE_DICT_FILE)
download_file(SIMILARITY_URL, SIMILARITY_FILE)

# ---------------------- Load Data ----------------------
if os.path.exists(MOVIE_DICT_FILE) and os.path.exists(SIMILARITY_FILE):
    try:
        movies_dict = pickle.load(open(MOVIE_DICT_FILE, 'rb'))
        movies = pd.DataFrame(movies_dict)
        similarity = pickle.load(open(SIMILARITY_FILE, 'rb'))
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.stop()
else:
    st.error("❌ Required data files not found. Please check the Google Drive links.")
    st.stop()

# TMDB API Key
TMDB_API_KEY = "46660c76c7ff58983b9f1d0bc425350e"

# ---------------------- TMDB API Functions ----------------------
@st.cache_data
def get_movie_id(movie_title):
    """Fetch movie ID from TMDB using the title"""
    url = f"https://api.themoviedb.org/3/search/movie?query={movie_title}&api_key={TMDB_API_KEY}"
    try:
        response = requests.get(url).json()
        if response and 'results' in response and len(response['results']) > 0:
            return response['results'][0]['id']
    except requests.exceptions.RequestException:
        st.warning("⚠️ Error fetching movie ID from TMDB.")
    return None

@st.cache_data
def fetch_movie_details(movie_id):
    """Fetch detailed movie information from TMDB"""
    if movie_id is None:
        return None

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    try:
        response = requests.get(url).json()
        if response:
            return {
                "title": response.get("title", "N/A"),
                "overview": response.get("overview", "No description available."),
                "poster": f"https://image.tmdb.org/t/p/w500{response.get('poster_path')}" if response.get(
                    "poster_path") else "https://via.placeholder.com/300x450?text=No+Image",
                "release_date": response.get("release_date", "N/A"),
                "rating": response.get("vote_average", "N/A"),
                "genres": ", ".join([genre["name"] for genre in response.get("genres", [])]),
            }
    except requests.exceptions.RequestException:
        st.warning("⚠️ Error fetching movie details from TMDB.")
    return None

# ---------------------- Recommendation Function ----------------------
def recommend(movie):
    """Get top 5 recommended movies with details"""
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movie_indices = sorted(enumerate(distances), key=lambda x: x[1], reverse=True)[1:6]
        recommended_movies = [movies.iloc[i[0]]['title'] for i in movie_indices]

        # Fetch details in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            movie_ids = list(executor.map(get_movie_id, recommended_movies))
            movie_details = list(executor.map(fetch_movie_details, movie_ids))

        return movie_details
    except Exception as e:
        st.error(f"❌ Error in Recommendation: {e}")
        return []

# ---------------------- Streamlit UI ----------------------
st.markdown("""
    <style>
    body {
        background: #121212;
        color: white;
        font-family: 'Poppins', sans-serif;
    }

    .main {
        background: rgba(20, 20, 20, 0.85);
        padding: 30px;
        border-radius: 15px;
        backdrop-filter: blur(8px);
        box-shadow: 0px 0px 20px rgba(255, 0, 150, 0.4);
    }

    .title {
        font-size: 40px;
        text-align: center;
        font-weight: bold;
        color: #ff0099;
        text-shadow: 0px 0px 20px rgba(255, 0, 150, 0.8);
    }

    .stSelectbox label {
        color: white;
        font-size: 16px;
    }

    .movie-card {
        background: linear-gradient(135deg, #222, #111);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        transition: transform 0.4s ease, box-shadow 0.4s;
        box-shadow: 0px 10px 30px rgba(255, 0, 150, 0.3);
    }
    .movie-card:hover {
        transform: scale(1.08);
        box-shadow: 0px 15px 40px rgba(255, 0, 150, 0.6);
    }

    .movie-card img {
        border-radius: 15px;
        width: 100%;
        transition: opacity 0.4s ease;
    }
    .movie-card:hover img {
        opacity: 0.8;
    }

    .movie-title {
        font-weight: bold;
        font-size: 20px;
        margin: 12px 0;
        color: #ff0099;
    }
    .movie-details {
        font-size: 14px;
        opacity: 0.8;
        color: #bbb;
    }

    .stButton>button {
        background: linear-gradient(45deg, #ff0099, #ff6600);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #ff6600, #ff0099);
        transform: scale(1.08);
    }
    </style>
    """,
            unsafe_allow_html=True
            )

st.markdown('<div class="title">🔥 Movie Recommender System</div>', unsafe_allow_html=True)

selected_movie_name = st.selectbox("🔍 Select a movie:", movies['title'].values)

if st.button("🎬 Get Recommendations"):
    with st.spinner("🔍 Fetching movie recommendations..."):
        recommended_movies = recommend(selected_movie_name)

    if recommended_movies:
        cols = st.columns(len(recommended_movies))  # Dynamically create columns

        for i, movie in enumerate(recommended_movies):
            if movie:
                with cols[i]:
                    st.markdown(
                        f"""
                        <div class="movie-card">
                            <img src="{movie['poster']}" alt="{movie['title']}">
                            <div class="movie-title">{movie['title']}</div>
                            <div class="movie-details">
                                ⭐ {movie['rating']} | 📅 {movie['release_date']} <br>
                                🎭 {movie['genres']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
