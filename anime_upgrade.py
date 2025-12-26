import pandas as pd
import numpy as np
import warnings
import os

warnings.filterwarnings('ignore')

class AnimeRecommendationSystem:
    def __init__(self):
        # Dataframes
        self.anime_df = None
        self.rating_df = None
        
        # Collaborative Metadata
        self.anime_matrix = None
        self.knn_model = None
        self.anime_id_to_index = {}
        self.index_to_anime_id = {}
        
        # Content Metadata
        self.tfidf_matrix = None
        self.vectorizer = None # Lazy load
        
    def load_data(self, anime_path, rating_path=None):
        """
        Load datasets with memory optimization.
        """
        # Specify dtypes to save memory (Default is int64/float64, we use int32/float32)
        anime_dtypes = {
            'anime_id': 'int32',
            'members': 'float32', # Some values might be NaN or large
            'rating': 'float32',
            'episodes': 'object'  # Can contain "Unknown"
        }
        
        rating_dtypes = {
            'user_id': 'int32',
            'anime_id': 'int32',
            'rating': 'int8'      # Ratings are -1 to 10
        }

        self.anime_df = pd.read_csv(anime_path, dtype=anime_dtypes)
        
        if rating_path and os.path.exists(rating_path):
            self.rating_df = pd.read_csv(rating_path, dtype=rating_dtypes, nrows=500000)
            
            # Filter noise immediately to save RAM
            # Remove users who didn't rate content (rating = -1)
            self.rating_df = self.rating_df[self.rating_df['rating'] >= 0]
            
            # Keep only users with > 50 ratings (Quality over Quantity)
            counts = self.rating_df['user_id'].value_counts()
            self.rating_df = self.rating_df[self.rating_df['user_id'].isin(counts[counts > 50].index)]
        else:
            self.rating_df = None
        
        # Optimize strings
        self.anime_df['name'] = self.anime_df['name'].astype('string')
        self.anime_df['genre'] = self.anime_df['genre'].astype('string')
        self.anime_df['type'] = self.anime_df['type'].astype('category')

    def preprocess_data(self):
        """
        Basic preprocessing
        """
        if self.anime_df is not None:
            # Helper for name search
            self.anime_df['name_lower'] = self.anime_df['name'].str.lower()
            
            # Fill NaN
            self.anime_df['genre'] = self.anime_df['genre'].fillna('')

    def build_models(self):
        """
        Builds both models.
        """
        self._build_content_model()
        self._build_collaborative_model()

    def _build_content_model(self):
        """
        Build Content-Based Model using TF-IDF.
        Lazy import sklearn to prevent import-time crashes.
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import linear_kernel
        
        # TF-IDF Matrix
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(self.anime_df['genre'])
        
        # Remove duplicates for mapping 
        self.anime_unique = self.anime_df.drop_duplicates(subset='name')
        self.indices = pd.Series(self.anime_unique.index, index=self.anime_unique['name']).drop_duplicates()

    def _build_collaborative_model(self):
        """
        Build Item-Based Composite Filtering Model using NearestNeighbors.
        Uses Scipy Sparse Matrix + Lazy Imports to avoid MemoryError.
        """
        if self.rating_df is None or self.anime_df is None:
            return

        # Lazy Import heavy libraries
        from sklearn.neighbors import NearestNeighbors
        from scipy.sparse import csr_matrix

        # Prepare data for sparse matrix
        # Optimize: Filter instead of Merge to save RAM
        valid_anime_ids = set(self.anime_df['anime_id'])
        self.rating_df = self.rating_df[self.rating_df['anime_id'].isin(valid_anime_ids)]
        
        # Create Sparse Matrix directly
        unique_users = self.rating_df['user_id'].unique()
        unique_animes = self.rating_df['anime_id'].unique()
        
        user_to_idx = {user: i for i, user in enumerate(unique_users)}
        anime_to_idx = {anime: i for i, anime in enumerate(unique_animes)}
        
        # Update lookup maps
        self.anime_id_to_index = anime_to_idx
        self.index_to_anime_id = {i: anime for anime, i in anime_to_idx.items()}
        
        # Create arrays
        user_indices = self.rating_df['user_id'].map(user_to_idx).values
        anime_indices = self.rating_df['anime_id'].map(anime_to_idx).values
        ratings = self.rating_df['rating'].values
        
        # Build Matrix
        self.anime_matrix = csr_matrix((ratings, (anime_indices, user_indices)), shape=(len(unique_animes), len(unique_users)))
        
        # Fit Model
        self.knn_model = NearestNeighbors(metric='cosine', algorithm='brute')
        self.knn_model.fit(self.anime_matrix)

    def get_recommendations(self, anime_title, top_n=10):
        """
        Get recommendations using Hybrid (Collab -> Content Fallback)
        """
        # 1. Find the anime
        search = self.anime_df[self.anime_df['name'].str.contains(anime_title, case=False, na=False)]
        if search.empty:
            return [], "error"
        
        target_anime = search.iloc[0]
        target_id = target_anime['anime_id']
        target_name = target_anime['name']
        
        # 2. Try Collaborative
        try:
            if self.knn_model and target_id in self.anime_id_to_index:
                idx = self.anime_id_to_index[target_id]
                distances, indices = self.knn_model.kneighbors(
                    self.anime_matrix[idx], n_neighbors=top_n+1)
                
                recommendations = []
                for i in range(1, len(distances.flatten())): # Skip 0 (itself)
                    neighbor_idx = indices.flatten()[i]
                    anime_id = self.index_to_anime_id[neighbor_idx]
                    
                    row = self.anime_df[self.anime_df['anime_id'] == anime_id].iloc[0]
                    recommendations.append(self._package_anime_data(row))
                    
                return recommendations, "collaborative"
        except Exception:
            pass
            
        # 3. Fallback to Content-Based
        try:
            from sklearn.metrics.pairwise import linear_kernel
            
            # Find index in unique set
            if target_name in self.indices:
                idx = self.indices[target_name]
                
                # Compute Similarity just for this vector (save RAM)
                cosine_sim = linear_kernel(self.tfidf_matrix[idx], self.tfidf_matrix).flatten()
                
                sim_scores = list(enumerate(cosine_sim))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                sim_scores = sim_scores[1:top_n+1]
                
                recommendations = []
                for i, score in sim_scores:
                    row = self.anime_unique.iloc[i]
                    recommendations.append(self._package_anime_data(row))
                    
                return recommendations, "content"
        except Exception:
            pass
            
        return [], "error"

    def get_categories(self):
        if self.anime_df is None: return []
        
        all_genres = []
        for genres in self.anime_df['genre'].dropna():
            if isinstance(genres, str):
                all_genres.extend([g.strip() for g in genres.split(',')])
                
        return sorted(list(set(all_genres)))

    def get_category_recommendations(self, category, top_n=10):
        if self.anime_df is None: return []
        
        mask = self.anime_df['genre'].str.contains(category, case=False, na=False)
        cat_df = self.anime_df[mask]
        
        if 'rating' in cat_df.columns:
            cat_df = cat_df.sort_values('rating', ascending=False)
            
        results = []
        for _, row in cat_df.head(top_n).iterrows():
            results.append(self._package_anime_data(row))
        return results

    def get_top_animes(self, top_n=12):
        """
        Get top animes by popularity (members) to use as default view
        """
        if self.anime_df is None: return []
        
        # Sort by members (popularity) or rating
        # Using members typically gives 'Trending/Popular' which is good for default
        # Ensure we have the column
        if 'members' in self.anime_df.columns:
             top_df = self.anime_df.sort_values('members', ascending=False).head(top_n)
        elif 'rating' in self.anime_df.columns:
             top_df = self.anime_df.sort_values('rating', ascending=False).head(top_n)
        else:
             top_df = self.anime_df.head(top_n)
             
        results = []
        for _, row in top_df.iterrows():
            results.append(self._package_anime_data(row))
        return results

    def _package_anime_data(self, row):
        return {
            "name": row['name'],
            "genre": row.get('genre', 'Unknown'),
            "rating": row.get('rating', 'N/A'),
            "type": row.get('type', 'TV'),
            "episodes": row.get('episodes', '?'),
            "id": row.get('anime_id', None)
        }