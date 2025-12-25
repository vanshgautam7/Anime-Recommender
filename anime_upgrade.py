import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AnimeRecommendationSystem:
    def __init__(self):
        self.anime_df = None
        self.rating_df = None
        self.tfidf_matrix = None
        self.cosine_sim = None
        self.vectorizer = TfidfVectorizer()
        self.scaler = StandardScaler()
        self.available_categories = []
        
    def load_data(self, anime_path, rating_path):
        """Load anime and rating datasets from CSV files"""
        self.anime_df = pd.read_csv(anime_path)
        self.rating_df = pd.read_csv(rating_path)

        print(f"✅ Loaded {len(self.anime_df)} anime entries")
        print(f"✅ Loaded {len(self.rating_df)} rating entries")
        
        return self.anime_df, self.rating_df
    
    def preprocess_data(self):
        """Clean and preprocess the data"""
        # Handle missing values in anime data
        text_columns = ['genre', 'type']
        for col in text_columns:
            if col in self.anime_df.columns:
                self.anime_df[col] = self.anime_df[col].fillna('Unknown')
        
        # Handle numerical columns in anime data
        numerical_cols = ['rating', 'members', 'episodes']
        for col in numerical_cols:
            if col in self.anime_df.columns:
                self.anime_df[col] = pd.to_numeric(self.anime_df[col], errors='coerce').fillna(0)
        
        # Extract and clean categories from genre column
        self._extract_categories()
        
        # Create combined features for content-based filtering
        feature_cols = []
        if 'genre' in self.anime_df.columns:
            feature_cols.append('genre')
        if 'type' in self.anime_df.columns:
            feature_cols.append('type')
            
        if feature_cols:
            self.anime_df['combined_features'] = self.anime_df[feature_cols].apply(
                lambda x: ' '.join(x.astype(str)), axis=1
            )
        
        # Clean rating data
        if self.rating_df is not None:
            self.rating_df = self.rating_df.dropna()
            rating_col = 'rating' if 'rating' in self.rating_df.columns else self.rating_df.columns[-1]
            self.rating_df[rating_col] = pd.to_numeric(self.rating_df[rating_col], errors='coerce')
            self.rating_df = self.rating_df.dropna()
        
        print("✅ Data preprocessing completed")
        
    def _extract_categories(self):
        """Extract unique categories from genre column"""
        all_genres = []
        if 'genre' in self.anime_df.columns:
            for genres in self.anime_df['genre'].dropna():
                if isinstance(genres, str) and genres != 'Unknown':
                    # Split by comma and clean each genre
                    genre_list = [g.strip() for g in genres.split(',')]
                    all_genres.extend(genre_list)
        
        # Get unique categories and sort them
        self.available_categories = sorted(list(set(all_genres)))
        print(f"✅ Extracted {len(self.available_categories)} unique categories")
    
    def display_available_categories(self):
        """Display all available categories in a clean format"""
        if not self.available_categories:
            print("❌ No categories found. Run preprocess_data() first.")
            return
        
        print("\n" + "="*60)
        print("📋 AVAILABLE ANIME CATEGORIES")
        print("="*60)
        # Display categories in columns for better readability
        cols = 3
        for i in range(0, len(self.available_categories), cols):
            row = self.available_categories[i:i+cols]
            formatted_row = [f"{j+i+1:2d}. {cat:<18}" for j, cat in enumerate(row)]
            print("  ".join(formatted_row))
        
        print("="*60)
        print(f"Total Categories: {len(self.available_categories)}")
        return self.available_categories
    
    def get_category_recommendations(self, category, top_n=10):
        """Get top anime recommendations for a specific category"""
        if not self.available_categories:
            return "❌ Categories not loaded. Run preprocess_data() first."
        
        # Check if category exists (case insensitive)
        category_lower = category.lower()
        matching_categories = [cat for cat in self.available_categories if cat.lower() == category_lower]
        
        if not matching_categories:
            # Try partial match
            partial_matches = [cat for cat in self.available_categories if category_lower in cat.lower()]
            if partial_matches:
                print(f"🔍 Did you mean one of these? {', '.join(partial_matches[:5])}")
            return f"❌ Category '{category}' not found."
        
        selected_category = matching_categories[0]
        
        # Filter anime by category
        category_anime = self.anime_df[
            self.anime_df['genre'].str.contains(selected_category, case=False, na=False)
        ].copy()
        
        if category_anime.empty:
            return f"❌ No anime found for category '{selected_category}'"
        
        # Sort by rating and members for best recommendations
        sort_columns = []
        if 'rating' in category_anime.columns:
            # Only consider anime with decent ratings (>= 5.0)
            category_anime = category_anime[category_anime['rating'] >= 5.0]
            sort_columns.append('rating')
        
        if 'members' in category_anime.columns:
            sort_columns.append('members')
        
        if sort_columns:
            category_anime = category_anime.sort_values(sort_columns, ascending=[False, False])
        
        # Select display columns
        display_cols = ['name']
        for col in ['genre', 'rating', 'type', 'episodes', 'members']:
            if col in category_anime.columns:
                display_cols.append(col)
        
        recommendations = category_anime.head(top_n)[display_cols].reset_index(drop=True)
        
        # Format the output nicely
        self._display_category_recommendations(selected_category, recommendations, top_n)
        
        return recommendations
    
    def _display_category_recommendations(self, category, recommendations, top_n):
        """Display category recommendations in a clean format"""
        print("\n" + "="*80)
        print(f"🎯 TOP {min(top_n, len(recommendations))} ANIME RECOMMENDATIONS FOR: {category.upper()}")
        print("="*80)
        
        if recommendations.empty:
            print("❌ No recommendations found for this category.")
            return
        
        for idx, row in recommendations.iterrows():
            print(f"\n{idx + 1:2d}. 📺 {row['name']}")
            print(f"    {'─' * (len(row['name']) + 5)}")
            
            if 'rating' in row:
                rating = row['rating']
                stars = "⭐" * int(rating) if rating > 0 else "No rating"
                print(f"    🌟 Rating: {rating}/10  {stars}")
            
            if 'type' in row:
                print(f"    📋 Type: {row['type']}")
            
            if 'episodes' in row:
                episodes = int(row['episodes']) if row['episodes'] > 0 else 'Unknown'
                print(f"    📺 Episodes: {episodes}")
            
            if 'members' in row:
                members = int(row['members']) if row['members'] > 0 else 0
                print(f"    👥 Members: {members:,}")
            
            if 'genre' in row:
                print(f"    🏷️  Genres: {row['genre']}")
        
        print("\n" + "="*80)
    
    def interactive_category_selection(self):
        """Interactive method for category selection"""
        self.display_available_categories()
        
        while True:
            print(f"\n🎮 Enter a category name (or 'quit' to exit):")
            user_input = input("➤ ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Thank you for using the Anime Recommendation System!")
                break
            
            if not user_input:
                print("❌ Please enter a valid category name.")
                continue
            
            print(f"\n🔍 Searching for top 10 anime in '{user_input}' category...")
            recommendations = self.get_category_recommendations(user_input, top_n=10)
            
            # Ask if user wants to continue
            print(f"\n💭 Would you like to search for another category? (y/n)")
            continue_choice = input("➤ ").strip().lower()
            if continue_choice not in ['y', 'yes']:
                print("👋 Thank you for using the Anime Recommendation System!")
                break
    
    def build_content_model(self):
        """Build content-based recommendation model using TF-IDF"""
        if 'combined_features' not in self.anime_df.columns:
            print("❌ No combined features found. Run preprocess_data() first.")
            return
            
        self.tfidf_matrix = self.vectorizer.fit_transform(self.anime_df['combined_features'])
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        print("✅ Content-based model built successfully")
    
    def get_content_recommendations(self, anime_title, top_n=10):
        """Get recommendations based on content similarity"""
        if self.cosine_sim is None:
            return "❌ Content model not built. Run build_content_model() first."
        
        name_col = 'name' if 'name' in self.anime_df.columns else self.anime_df.columns[1]
        try:
            idx = self.anime_df[self.anime_df[name_col].str.contains(anime_title, case=False, na=False)].index[0]
        except IndexError:
            return f"❌ Anime '{anime_title}' not found in dataset"
        
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        anime_indices = [i[0] for i in sim_scores[1:top_n+1]]
        
        display_cols = []
        for col in ['name', 'genre', 'rating', 'type']:
            if col in self.anime_df.columns:
                display_cols.append(col)
        
        recommendations = self.anime_df.iloc[anime_indices][display_cols].copy()
        recommendations['similarity_score'] = [sim_scores[i+1][1] for i in range(min(top_n, len(anime_indices)))]
        
        return recommendations

def main():
    print("🎌 ANIME RECOMMENDATION SYSTEM")
    print("="*50)
    
    # Initialize the recommendation system
    recommender = AnimeRecommendationSystem()
    
    # Load your CSV files (update these paths to your actual file locations)
    anime_path = r"C:\MCA\Vs Code Python\Anime Recommender\anime.csv"
    rating_path = r"C:\MCA\Vs Code Python\Anime Recommender\rating.csv"
    
    try:
        print("📂 Loading data...")
        recommender.load_data(anime_path, rating_path)
        
        print("\n🔧 Preprocessing data...")
        recommender.preprocess_data()
        
        print("\n🏗️  Building content model...")
        recommender.build_content_model()
        
        print("\n🚀 System ready!")
        
        # Start interactive category selection
        recommender.interactive_category_selection()
        
    except FileNotFoundError as e:
        print(f"❌ Error: Could not find the CSV files. Please check the file paths.")
        print(f"    Expected files: {anime_path} and {rating_path}")
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()