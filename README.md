🎬 Aniora — AI-Powered Anime Recommendation System

Discover your next anime obsession with intelligent recommendations and a cinematic UI.

Aniora is an end-to-end anime recommendation platform that combines machine learning, real-time anime data, and a premium Apple TV–inspired interface to help users find anime they’ll genuinely love.

✨ Key Features

🎯 Hybrid Recommendation Engine

✨ Collaborative Filtering (user–anime similarity)

📚 Content-Based Filtering (genre & metadata)

🔁 Smart fallback strategy for cold-start anime

🧠 Explainable AI

Clear labels showing which model generated the recommendation

Transparent and interview-friendly logic

🎨 Premium UI (Apple TV–Inspired)

Dark cinematic theme

Interactive anime cards

Smooth hover effects

Clean, distraction-free layout

🖼️ Live Anime Posters

Integrated with Jikan API (MyAnimeList)

Fetches real-time anime images & metadata

⚡ Optimized Performance

Cached models and API calls using Streamlit

Fast response even with large datasets

🛠️ Tech Stack

Python

Streamlit

Pandas & NumPy

SciPy (Sparse Matrices)

Scikit-Learn

Jikan API

HTML & CSS (Custom Styling)

🧩 How It Works
1️⃣ Collaborative Filtering

Users who have similar anime preferences are grouped together using a User × Anime sparse matrix. Recommendations are generated based on what similar users enjoyed.

2️⃣ Content-Based Filtering

For anime with insufficient user ratings, recommendations fall back to genre and metadata similarity.

3️⃣ Hybrid Strategy

The system automatically chooses the best model and displays a badge:

✨ Collaborative Intelligence

📚 Content-Based Match

📸 Screenshots

<img width="1919" height="979" alt="image" src="https://github.com/user-attachments/assets/e7633106-963a-46af-a4cb-d0a47219edfd" />


<img width="1919" height="974" alt="image" src="https://github.com/user-attachments/assets/4b00fcb5-7834-4379-bd8f-dfde3d03c4d7" />


<img width="1919" height="978" alt="image" src="https://github.com/user-attachments/assets/e8bf92a2-b1cd-4135-b24c-bf4a02b670c4" />


🚀 Getting Started
pip install -r requirements.txt
streamlit run app.py


Open in browser:

http://localhost:8501

📁 Project Structure
Anime-Recommender/
├── app.py
├── anime_upgrade.py
├── anime.csv
├── rating.csv
├── hero_bg.jpg
├── README.md
├── changelog.md
├── LICENSE
├── .gitignore




