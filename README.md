# Aniora — AI-Powered Anime Recommendation System

Discover your next anime obsession with intelligent recommendations and a cinematic UI.
Aniora is an end-to-end anime recommendation platform that combines machine learning, real-time anime data, and a premium Apple TV–inspired interface to help users find anime they’ll genuinely love.

# Key Features

 Hybrid Recommendation Engine
 Collaborative Filtering (user–anime similarity)
 Content-Based Filtering (genre & metadata)
 Smart fallback strategy for cold-start anime


# Live Anime Posters

Integrated with Jikan API (MyAnimeList)

Fetches real-time anime images & metadata

# Optimized Performance

Cached models and API calls using Streamlit

Fast response even with large datasets

# Tech Stack
Python
Streamlit
Pandas & NumPy
SciPy (Sparse Matrices)
Scikit-Learn
Jikan API
HTML & CSS (Custom Styling)

# Dataset Note:
The recommendation model is trained on a historical anime dataset.
Live metadata (images, ratings, popularity) is fetched in real time via MyAnimeList API.

 # Screenshots

<img width="1919" height="979" alt="image" src="https://github.com/user-attachments/assets/e7633106-963a-46af-a4cb-d0a47219edfd" />


<img width="1919" height="974" alt="image" src="https://github.com/user-attachments/assets/4b00fcb5-7834-4379-bd8f-dfde3d03c4d7" />


<img width="1919" height="978" alt="image" src="https://github.com/user-attachments/assets/e8bf92a2-b1cd-4135-b24c-bf4a02b670c4" />


# Getting Started
pip install -r requirements.txt
streamlit run app.py
Open in browser: http://localhost:8501




