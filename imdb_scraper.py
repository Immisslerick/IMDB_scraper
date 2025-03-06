import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_imdb_top_movies():
    # URL of IMDb Top 250 movies
    url = "https://www.imdb.com/chart/top/"
    
    # Headers to mimic browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # Send GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Initialize lists to store movie details
        movies_data = []
        
        # Find all movie entries in the new IMDb structure
        movie_elements = soup.find_all('h3', class_='ipc-title__text')
        
        for movie in movie_elements:
            try:
                # The text format is usually: "1. Movie Name (YYYY)"
                text = movie.text.strip()
                if not text or '. ' not in text:
                    continue
                
                # Split the ranking and movie details
                parts = text.split('. ', 1)
                if len(parts) < 2:
                    continue
                    
                movie_details = parts[1]
                
                # Extract year from the end if present
                year = ''
                title = movie_details
                if movie_details.endswith(')'):
                    year_start = movie_details.rfind('(')
                    if year_start != -1:
                        year = movie_details[year_start + 1:-1]
                        title = movie_details[:year_start].strip()
                
                # Find the parent container to get rating
                parent = movie.find_parent('div', class_='ipc-metadata-list-summary-item__c')
                rating = ''
                rating_count = ''
                
                if parent:
                    # Try to find rating
                    rating_elem = parent.find('span', class_='ipc-rating-star--imdb')
                    if rating_elem:
                        rating = rating_elem.text.strip().split()[0]
                    
                    # Try to find rating count
                    count_elem = parent.find('span', class_='ipc-rating-star--voteCount')
                    if count_elem:
                        rating_count = count_elem.text.strip()
                
                movies_data.append({
                    'Title': title,
                    'Year': year,
                    'Rating': rating,
                    'Number of Ratings': rating_count
                })
                
            except Exception as e:
                print(f"Error processing movie: {e}")
                continue
        
        return movies_data
    
    except Exception as e:
        print(f"Error scraping IMDb: {e}")
        return None

def save_to_csv(movies_data):
    if not movies_data:
        return False
    
    # Create DataFrame
    df = pd.DataFrame(movies_data)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'imdb_top_movies_{timestamp}.csv'
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Data saved successfully to {filename}")
    return True

def main():
    print("Starting IMDb scraping...")
    movies_data = scrape_imdb_top_movies()
    
    if movies_data:
        print(f"Successfully scraped {len(movies_data)} movies")
        save_to_csv(movies_data)
    else:
        print("Failed to scrape movie data")

if __name__ == "__main__":
    main()
