import streamlit as st
import pandas as pd
import os
import requests
import time
import base64
import concurrent.futures
from anime_upgrade import AnimeRecommendationSystem

# Page Configuration
st.set_page_config(
    page_title="Aniora",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    .hero-bg {{
        background-image: url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
        background-position: center; 
        opacity: 1.0;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Apple TV Style CSS - Minimal, Dark, Interactive
st.markdown("""
    <style>
    /* Global Reset & Dark Theme */
    .stApp {
        background-color: #000000;
        color: #ffffff;
        font-family: -apple-system, sans-serif;
    }
    
    /* Hide standard details */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    /* Animation Keyframes */
    @keyframes zoomEffect {
        0% { transform: scale(1.0); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1.0); }
    }

    /* Hero Section Styling - Immersive */
    .hero-container {
        position: relative;
        height: 70vh; /* Taller hero */
        width: 100%;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        /* Seamless blend into body */
        background: black; 
        margin-bottom: 0px;
    }
    
    .hero-bg {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 0;
        /* No Blur, Full Color */
        filter: brightness(0.7); 
        /* Vignette mask for seamless blending */
        mask-image: radial-gradient(circle at center, black 40%, transparent 100%);
        -webkit-mask-image: radial-gradient(circle at center, black 40%, transparent 100%);
        animation: zoomEffect 20s infinite ease-in-out;
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        text-align: center;
        padding-top: 40px; /* Space for the bigger logo */
    }
    
    /* DYNAMIC ACTION LOGO */
    /* Idea 1: Clean Streamer (Minimalist & Bold) */
    /* Idea 2: Bold & Bordered (User Request) */
    h1 {
        font-family: Arial Black, Impact, sans-serif;
        font-weight: 900;
        font-size: 16rem; /* Increased size significantly */
        font-style: italic; /* Optional: keeps it dynamic */
        
        /* White Fill */
        color: #FFFFFF;
        -webkit-text-fill-color: #FFFFFF;
        
        /* Black Border */
        -webkit-text-stroke: 4px black; 
        paint-order: stroke fill;
        
        /* Shadow for pop */
        text-shadow: 6px 6px 0px #000000;
        
        margin-bottom: 0px;
        line-height: 1.1;
        text-transform: uppercase;
        padding: 10px 0;
    }

    /* Remove previous slash effects */
    h1::after {
        content: none;
    }
    
    p.subtitle {
        color: #FFFFFF;
        font-family: Arial Black, Impact, sans-serif; /* Matching bold font */
        font-size: 2rem; /* Increased size */
        font-weight: 800;
        margin-top: 5px;
        opacity: 1.0;
        
        /* Black Border for Subtitle */
        -webkit-text-stroke: 1.5px black;
        text-shadow: 3px 3px 0px #000000;
        letter-spacing: 1px;
    }
    
    /* Navigation Pills - Centered */
    div[data-testid="stRadio"] {
        background: rgba(40, 40, 40, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 50px;
        padding: 5px;
        display: inline-flex;
        border: 1px solid rgba(255,255,255,0.1);
        margin: 0px auto 0px auto; /* Zero bottom margin */
        width: fit-content;
    }

    /* Tighten Content Layout - Nuclear Option */
    .block-container {
        padding-top: 0rem !important; /* Move up even more */
        padding-bottom: 0rem !important;
    }
    
    h2, h3, p {
        margin: 0px !important;
        padding: 0px !important;
    }
    
    /* Specific overrides for headers to ensure visibility */
    h2 {
        font-size: 1.5rem !important;
        margin-bottom: 5px !important;
        margin-top: 5px !important;
    }

    div[data-testid="stVerticalBlock"] > div {
        gap: 0rem !important; /* Zero gap between components */
        padding-bottom: 0px !important;
    }
    
    .stSelectbox {
        margin-top: 0px !important;
    }
    
    .stSelectbox label {
        margin-bottom: 5px !important; /* Restored spacing for safety */
        font-size: 0.9rem !important;
        color: #dddddd !important;
    }

    /* Cards */
    .movie-card {
        position: relative;
        width: 100%;
        aspect-ratio: 2/3;
        border-radius: 12px;
        overflow: hidden;
        cursor: pointer;
        transition: transform 0.3s ease;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 20px;
    }
    
    .movie-card:hover {
        transform: scale(1.1) translateY(-10px); /* Apple TV pop effect */
        z-index: 100;
        box-shadow: 0 30px 60px rgba(0,0,0,0.8);
        border-color: rgba(255,255,255,0.4);
    }
    
    .movie-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.4s ease;
    }
    
    .movie-card:hover .movie-img {
        filter: brightness(0.4);
    }
    
    .movie-info {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center; /* Center Vertically */
        align-items: center;     /* Center Horizontally */
        padding: 20px;
        opacity: 0;
        transition: opacity 0.3s ease;
        text-align: center;
        background: rgba(0,0,0,0.85); /* Darker overlay for readability */
        backdrop-filter: blur(4px);   /* Glassmorphism blur */
    }
    
    .movie-card:hover .movie-info {
        opacity: 1;
    }
    
    .movie-title {
        font-size: 1.4rem;  /* Larger Title */
        font-weight: 800;   /* Bold */
        color: #ffffff;
        margin-bottom: 5px;
        line-height: 1.2;
        text-transform: uppercase; /* Unique style */
        letter-spacing: 1px;
        text-shadow: 0 4px 8px rgba(0,0,0,0.5);
    }
    .movie-meta {
        font-size: 0.95rem;
        color: #e0e0e0;
        font-weight: 400;
        margin-bottom: 12px;
        letter-spacing: 0.5px;
    }
    .match-badge {
        background: #ffffff;
        color: #000;
        padding: 6px 14px; /* Larger pill */
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 900;
        margin-top: 5px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Clean up inputs */
    .stTextInput > div > div {
        background-color: rgba(255,255,255,0.1) !important;
        border-radius: 12px;
        color: #fff;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- Jikan API Integration ---
# --- Jikan API Integration ---
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_anime_image(anime_data):
    """
    Fetch anime image. Prioritizes ID lookup, falls back to name.
    anime_data is a dict with 'id' and 'name'.
    """
    anime_id = anime_data.get('id')
    anime_name = anime_data.get('name')
    
    # 1. ID Lookup (Best)
    if anime_id and str(anime_id) != 'nan':
        url = f"https://api.jikan.moe/v4/anime/{anime_id}"
    else:
        # 2. Name Lookup (Fallback)
        url = f"https://api.jikan.moe/v4/anime?q={anime_name}&limit=1"
        
    try:
        # Rate limit handling is done in the worker pool, but safety sleep here
        time.sleep(0.1) 
        response = requests.get(url, timeout=4)
        
        if response.status_code == 200:
            data = response.json()
            # Handle different response structures for ID vs Search
            item = data['data'] if 'data' in data else None
            
            # Search endpoint returns a list in 'data'
            if isinstance(item, list):
                item = item[0] if item else None
                
            if item:
                return {
                    "image": item['images']['jpg']['large_image_url'],
                    "title": item['title'],
                    "mal_id": item['mal_id']
                }
    except Exception:
        pass

    # Fallback
    return {
        "image": "https://via.placeholder.com/225x320/1a1a1a/cccccc?text=No+Image",
        "title": anime_name,
        "mal_id": None
    }

def fetch_images_parallel(recommendations):
    """
    Fetch all images in parallel.
    Respects Jikan API limit (approx 3 req/sec) using max_workers=3
    """
    results = [None] * len(recommendations)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Create a dict of {future: index} to Map results back to correct order
        future_to_index = {
            executor.submit(fetch_anime_image, anime): i 
            for i, anime in enumerate(recommendations)
        }
        
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                data = future.result()
                results[index] = data
            except Exception:
                results[index] = {
                    "image": "https://via.placeholder.com/225x320/1a1a1a/cccccc?text=Error",
                    "title": recommendations[index]['name']
                }
                
    return results


import random

# --- Anime Quotes ---
ANIME_QUOTES = [
    "Power comes in response to a need, not a desire. You have to create that need. - Goku",
    "Simplicity is the easiest path to true beauty. - Seishuu Handa",
    "In this world, wherever there is light - there are also shadows. - Ryuk",
    "Fear is not evil. It tells you what your weakness is. - Gildarts",
    "Whatever you lose, you'll find it again. - Kenshin Himura",
    "Hard work betrays none, but dreams betray many. - Hachiman",
    "To defeat evil, I shall become a greater evil. - Lelouch",
    "A dropout will beat a genius through hard work. - Rock Lee",
    "If you don't take risks, you can't create a future. - Luffy"
]

# --- Recommender System ---
@st.cache_resource(show_spinner=False)
def _get_recommender_system_fresh():
    # Check for files

    current_dir = os.path.dirname(os.path.abspath(__file__))
    anime_path = os.path.join(current_dir, "data", "anime.csv")
    rating_path = os.path.join(current_dir, "rating.csv") # Assuming rating.csv is still in root or change to data if moved
    
    # If rating.csv might also be in data, check there too or just standardise
    # For now, per instructions, we moved anime.csv to data/. rating.csv is large and user likely excluded it or it is in root.
    # Let's check root first as per original, but if not found, check data/ just in case.
    
    if not os.path.exists(anime_path):
        # Fallback to root just in case locally it wasn't moved yet or similar
        anime_path_root = os.path.join(current_dir, "anime.csv")
        if os.path.exists(anime_path_root):
             anime_path = anime_path_root
        else:
             return None

    # Flexible rating path
    final_rating_path = None
    if os.path.exists(rating_path):
        final_rating_path = rating_path
    
    sys = AnimeRecommendationSystem()
    sys.load_data(anime_path, final_rating_path)
    sys.preprocess_data()
    sys.build_models()
    return sys

def get_recommender_v3():
    # Only show intro on first load
    if 'intro_shown' not in st.session_state:
        st.session_state.intro_shown = False
        
    quote = random.choice(ANIME_QUOTES)
    
    if not st.session_state.intro_shown:
        # --- Custom Loading Screen ---
        loader_placeholder = st.empty()
        with loader_placeholder.container():
            # Centered Quote Display
            st.markdown(f"""
                <div style="height: 70vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; animation: fade 2s infinite;">
                    <h2 style="font-size: 2.5rem; font-weight: 800; color: #fff; margin-bottom: 20px; font-style: italic;">
                        "{quote.split(' - ')[0]}"
                    </h2>
                    <p style="font-size: 1.2rem; color: #a0a0a0; font-family: monospace;">
                        - {quote.split(' - ')[-1]}
                    </p>
                    <div style="margin-top: 40px; width: 50px; height: 50px; border: 3px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: #fff; animation: spin 1s ease-in-out infinite;"></div>
                </div>
                <style>
                    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
                    @keyframes fade {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} }}
                </style>
            """, unsafe_allow_html=True)
            
            # Artificial delay to let the quote breathe
            time.sleep(2.5)
            
        # Clear Loader and mark as shown
        loader_placeholder.empty()
        st.session_state.intro_shown = True

    # Actual Loading (Always fetch fresh/cached)
    recommender = _get_recommender_system_fresh()
    
    if recommender is None:
         st.error("Data files not found.")
         return None

    return recommender

# --- UI Components ---
def render_hero_section():
    st.markdown("""
        <div class="hero-container">
            <div class="hero-bg"></div>
            <div class="hero-content">
                <h1>Aniora</h1>
                <p class="subtitle">Discover your next obsession.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Inject background image
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(current_dir, "hero_bg.jpg")
        if os.path.exists(bg_path):
            set_background(bg_path)
    except Exception:
        pass

def render_movie_grid(recommendations, model_type=None):
    """
    Render grid of anime cards.
    Args:
        recommendations: List of dicts (from anime_upgrade.py)
        model_type: str "collaborative" or "content" (optional)
    """
    if not recommendations:
        st.error("No recommendations found.")
        return

    # Badge Logic
    badge_html = ""
    if model_type == "collaborative":
        badge_html = '<div style="text-align:center;margin-bottom:20px;"><span style="background:rgba(40, 167, 69, 0.2);color:#28a745;padding:6px 12px;border-radius:20px;font-size:0.9rem;border:1px solid #28a745;font-weight:600;">✨ Collaborative Intelligence</span></div>'
    elif model_type == "content":
        badge_html = '<div style="text-align:center;margin-bottom:20px;"><span style="background:rgba(108, 117, 125, 0.2);color:#adb5bd;padding:6px 12px;border-radius:20px;font-size:0.9rem;border:1px solid #6c757d;font-weight:600;">📚 Content-Based Match</span></div>'

    if model_type:
        st.markdown(badge_html, unsafe_allow_html=True)
    
    # 1. Parallel Fetch (Fast!)
    # We pass the full anime dicts (which have 'id' and 'name')
    with st.spinner("Loading visuals..."):
        image_data_list = fetch_images_parallel(recommendations)
    
    # Grid Layout
    cols = st.columns(5) 
    for idx, anime in enumerate(recommendations):
        col_idx = idx % 5
        
        # Prepare Data
        # Retrieve pre-fetched image data
        img_info = image_data_list[idx]
        img_url = img_info['image']
        title = img_info['title'] # Use API title if available, or fallback
        
        rating = anime.get('rating', 'N/A')
        try:
            if rating != 'N/A':
                 rating = f"{float(rating):.2f}"
        except:
            pass
            
        eps = anime.get('episodes', '?')
        kind = anime.get('type', 'TV')
        
        with cols[col_idx]:
            card_html = f"""
            <div class="movie-card">
                <img src="{img_url}" class="movie-img" loading="lazy">
                <div class="movie-info">
                    <div class="movie-title">{title}</div>
                    <div class="movie-meta">{kind} • {eps} eps</div>
                    <div class="match-badge">⭐ {rating}</div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

def main():
    recommender = get_recommender_v3()
    if not recommender:
        return

    # Render Hero
    render_hero_section()

    # Navigation
    mode = st.radio("Navigation", ["Browse Categories", "Search Title"], horizontal=True, label_visibility="collapsed")

    if mode == "Browse Categories":
        st.markdown("## 📂 Browse by Category")
        categories = recommender.get_categories()
        
        # Add a default option for Top Watched
        options = ["🔥 Top Watched"] + categories if categories else []
        
        if options:
            selected_category = st.selectbox("Select Genre", options)
            
            if selected_category == "🔥 Top Watched":
                 st.markdown("### 🔥 Most Popular on Aniora")
                 results = recommender.get_top_animes(top_n=15)
                 render_movie_grid(results, model_type="content")
            
            elif selected_category:
                results = recommender.get_category_recommendations(selected_category, top_n=15)
                render_movie_grid(results, model_type="content") 
    
    elif mode == "Search Title":
        st.markdown("## 🔍 Find Similar Anime")
        
        # Search Box
        anime_list = recommender.anime_df['name'].tolist() if recommender.anime_df is not None else []
        selected_anime = st.selectbox("Enter Anime Title", [""] + anime_list)
        
        if selected_anime:
            with st.spinner(f"Finding matches for {selected_anime}..."):
                # Get recommendations + model type return
                results, model_used = recommender.get_recommendations(selected_anime, top_n=15)
                render_movie_grid(results, model_type=model_used)

    # DEFAULT VIEW (Bottom of main)
    # If in Browse Categories but just started, show Trending
    if mode == "Browse Categories" and 'selected_category' not in locals():
         # Logic: If selectbox hasn't been used or is default
         pass 

if __name__ == "__main__":
    main()
