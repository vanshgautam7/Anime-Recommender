# Make sure rating is numeric
anime_df['rating'] = pd.to_numeric(anime_df['rating'], errors='coerce')

# Drop NaN ratings
anime_df = anime_df.dropna(subset=['rating'])

# Sort by rating in descending order
top_10_anime = anime_df.sort_values(by='rating', ascending=False).head(10)

print("Top 10 Anime by Rating:")
print(top_10_anime[['name', 'rating', 'genre', 'type', 'episodes']])