"""Configuration for Lowkey scraper - cities and query patterns."""

# Top 10 most visited cities
TARGET_CITIES = [
    "Bangkok",
    "Hong Kong", 
    "London",
    "Macau",
    "Istanbul",
    "Dubai",
    "Rome",
    "Antalya",
    "Paris",
    "Kuala Lumpur"
]

# Query patterns that yield high-quality results
# {city} will be replaced with each city name
QUERY_PATTERNS = [
    # Food & Drink
    "{city} cafe recommendations",
    "{city} best restaurants local",
    "{city} hidden gem food",
    "{city} street food must try",
    "{city} best bars nightlife",
    "{city} coffee shops work",
    "{city} brunch spots",
    "{city} cheap eats budget",
    "{city} fine dining worth it",
    "{city} rooftop bars",
    
    # Activities & Culture
    "{city} hidden gems tourists miss",
    "{city} local favorites avoid crowds",
    "{city} best neighborhoods explore",
    "{city} things to do off beaten path",
    "{city} best markets shopping",
    "{city} museums worth visiting",
    "{city} viewpoints sunset",
    "{city} day trips recommendations",
    
    # Accommodation
    "{city} best areas to stay",
    "{city} boutique hotels recommendations",
    "{city} hostels backpacker",
]

# Settings
POSTS_PER_QUERY = 10  # Scrape top 5 posts per query
DELAY_BETWEEN_REQUESTS = 5  # Seconds between Reddit requests
VALIDATE_WITH_GEMINI = True  # Use Gemini to validate posts