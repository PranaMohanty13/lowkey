"""Reddit scraper - search and scrape posts with comments."""
import sys
import time
import re
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent / "YARS" / "src"))
from yars.yars import YARS


class RedditScraper:
    """Scraper for Reddit posts with full comment data."""
    
    def __init__(self):
        self.miner = YARS()
    
    def search_and_scrape(
        self,
        search_query: str,
        limit: int = 10,
        delay: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Search Reddit and scrape posts with full details.
        
        Args:
            search_query: Search term (e.g., "paris cafe recommendations")
            limit: Max posts to scrape
            delay: Seconds between requests
        
        Returns:
            List of post data with all required fields for harvester
        """
        print(f"\n🔍 Searching: '{search_query}'")
        
        results = self.miner.search_reddit(search_query, limit=limit)
        print(f"   Found {len(results)} results")
        
        scraped_posts = []
        for i, result in enumerate(results[:limit], 1):
            title = result.get('title', 'No title')
            link = result.get('link', '')
            
            print(f"   [{i}/{limit}] {title[:70]}")
            
            try:
                if 'reddit.com' not in link:
                    print(f"      ⚠️ Not a Reddit link")
                    continue
                
                permalink = link.split('reddit.com')[1]
                post_details = self.miner.scrape_post_details(permalink)
                
                if not post_details:
                    print(f"      ❌ No details returned")
                    continue
                
                subreddit = self._extract_subreddit(permalink)
                num_comments = len(post_details.get('comments', []))
                
                post_data = {
                    'title': title,
                    'body': post_details.get('body', ''),
                    'comments': post_details.get('comments', []),
                    'url': link,
                    'permalink': permalink,
                    'subreddit': subreddit,
                    'num_comments': num_comments,
                    'search_query': search_query,
                }
                
                scraped_posts.append(post_data)
                print(f"      ✅ {num_comments} comments")
                
                time.sleep(delay)
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
                continue
        
        print(f"\n   ✅ Scraped {len(scraped_posts)}/{limit} posts")
        
        return scraped_posts
    
    def has_extractable_content(self, post_data: Dict) -> bool:
        """Check if post likely contains place recommendations."""
        
        text = post_data.get('body', '') or ''
        
        comments = post_data.get('comments', [])
        if comments:
            sorted_comments = sorted(
                comments,
                key=lambda c: c.get('upvotes', 0),
                reverse=True
            )[:15]
            text += ' ' + ' '.join(c.get('body', '') for c in sorted_comments)
        
        # Place name patterns
        place_patterns = [
            r'\b[A-Z][a-z]+ (?:Cafe|Coffee|Restaurant|Bar|Bistro|Shop|Hotel|Museum)\b',
            r'\bcalled [A-Z][a-z]+',
            r'\btry [A-Z][a-z]+',
            r'\bvisit [A-Z][a-z]+',
            r'\brecommend [A-Z][a-z]+',
        ]
        
        for pattern in place_patterns:
            if re.search(pattern, text):
                return True
        
        if len(text) < 100:
            return False
        
        travel_keywords = ['cafe', 'coffee', 'restaurant', 'bar', 'food', 'place', 'spot', 'gem', 'local']
        if any(kw in text.lower() for kw in travel_keywords):
            return True
        
        return False
    
    def _extract_subreddit(self, permalink: str) -> str:
        """Extract subreddit name from permalink."""
        try:
            parts = permalink.split('/')
            if len(parts) >= 3 and parts[1] == 'r':
                return parts[2]
        except:
            pass
        return 'unknown'


if __name__ == "__main__":
    scraper = RedditScraper()
    
    # Test with proven high-relevance query
    posts = scraper.search_and_scrape(
        search_query="bangkok restaurant recommendations",
        limit=5
    )
    
    print(f"\n{'='*60}")
    print(f"📊 Results: {len(posts)} posts")
    print(f"{'='*60}")
    
    # Show sample
    if posts:
        print(f"\nSample post:")
        p = posts[0]
        print(f"  Title: {p['title']}")
        print(f"  Subreddit: r/{p['subreddit']}")
        print(f"  Comments: {p['num_comments']}")
        print(f"  Has extractable content: {scraper.has_extractable_content(p)}")