"""Main harvester: Reddit → Validate → Extract places."""
import sys
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from reddit_scraper import RedditScraper
from gemini_validator import GeminiValidator
from place_extractor import PlaceExtractor
from config import TARGET_CITIES, QUERY_PATTERNS, POSTS_PER_QUERY, DELAY_BETWEEN_REQUESTS, VALIDATE_WITH_GEMINI


class Harvester:
    """Orchestrates the full Reddit harvesting pipeline."""
    
    def __init__(self):
        self.scraper = RedditScraper()
        self.validator = GeminiValidator()
        self.extractor = PlaceExtractor()
        self.output_dir = Path(__file__).parent / "data"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def harvest_city(
        self,
        city: str,
        query_patterns: List[str] = QUERY_PATTERNS,
        posts_per_query: int = POSTS_PER_QUERY,
        validate: bool = VALIDATE_WITH_GEMINI
    ) -> Dict:
        """
        Harvest all places for a single city.
        
        Returns:
            Dict with 'city', 'posts_count', 'places'
        """
        print(f"\n{'='*70}")
        print(f"🌆 HARVESTING: {city.upper()}")
        print(f"{'='*70}")
        
        all_validated_posts = []
        
        # Generate queries for this city
        queries = [pattern.format(city=city) for pattern in query_patterns]
        
        for qi, query in enumerate(queries, 1):
            print(f"\n[{qi}/{len(queries)}] Query: '{query}'")
            print("-" * 50)
            
            # Step 1: Search and scrape
            posts = self.scraper.search_and_scrape(
                search_query=query,
                limit=posts_per_query,
                delay=DELAY_BETWEEN_REQUESTS
            )
            
            if not posts:
                print(f"   ⚠️ No posts found")
                continue
            
            # Step 2: Quick content filter
            promising = [p for p in posts if self.scraper.has_extractable_content(p)]
            print(f"   📋 {len(promising)}/{len(posts)} passed content filter")
            
            if not promising:
                continue
            
            # Step 3: Gemini validation (optional)
            if validate:
                validated = []
                for post in promising:
                    result = self.validator.validate_post(post)
                    if result['has_recommendations']:
                        validated.append(post)
                print(f"   ✅ {len(validated)}/{len(promising)} validated by Gemini")
                all_validated_posts.extend(validated)
            else:
                all_validated_posts.extend(promising)
        
        # Step 4: Extract places from all validated posts
        places = []
        if all_validated_posts:
            print(f"\n{'='*50}")
            print(f"🎯 EXTRACTING PLACES FROM {len(all_validated_posts)} POSTS")
            print(f"{'='*50}")
            
            places = self.extractor.extract_from_posts(all_validated_posts)
        
        return {
            'city': city,
            'posts_count': len(all_validated_posts),
            'places': places
        }
    
    def harvest_all_cities(
        self,
        cities: List[str] = TARGET_CITIES,
        save_per_city: bool = True
    ) -> Dict:
        """
        Harvest places for all target cities.
        
        Args:
            cities: List of cities to harvest
            save_per_city: Save separate JSON per city
        
        Returns:
            Combined results dict
        """
        start_time = datetime.now()
        
        print(f"\n{'#'*70}")
        print(f"🌍 LOWKEY HARVESTER - BATCH RUN")
        print(f"{'#'*70}")
        print(f"Cities: {len(cities)}")
        print(f"Query patterns: {len(QUERY_PATTERNS)}")
        print(f"Total queries: {len(cities) * len(QUERY_PATTERNS)}")
        print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_places = []
        city_stats = []
        
        for ci, city in enumerate(cities, 1):
            print(f"\n\n{'#'*70}")
            print(f"CITY {ci}/{len(cities)}: {city}")
            print(f"{'#'*70}")
            
            result = self.harvest_city(city)
            
            if result['places']:
                all_places.extend(result['places'])
                
                # Save per-city JSON
                if save_per_city:
                    city_file = self.output_dir / "cities" / f"{city.lower().replace(' ', '_')}.json"
                    city_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(city_file, 'w', encoding='utf-8') as f:
                        json.dump(result['places'], f, indent=2, ensure_ascii=False)
                    print(f"\n💾 Saved {len(result['places'])} places to: {city_file}")
            
            city_stats.append({
                'city': city,
                'posts': result['posts_count'],
                'places': len(result['places'])
            })
        
        # Save combined results
        combined_file = self.output_dir / "all_places.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(all_places, f, indent=2, ensure_ascii=False)
        
        # Save stats
        end_time = datetime.now()
        duration = end_time - start_time
        
        stats = {
            'run_date': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration_minutes': round(duration.total_seconds() / 60, 1),
            'total_cities': len(cities),
            'total_places': len(all_places),
            'cities': city_stats
        }
        
        stats_file = self.output_dir / "harvest_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        # Print summary
        self._print_summary(stats, all_places)
        
        return {
            'stats': stats,
            'places': all_places
        }
    
    def _print_summary(self, stats: Dict, places: List[Dict]):
        """Print harvest summary."""
        
        print(f"\n\n{'#'*70}")
        print(f"🎉 HARVEST COMPLETE")
        print(f"{'#'*70}")
        print(f"Duration: {stats['duration_minutes']} minutes")
        print(f"Total places: {stats['total_places']}")
        
        print(f"\n📊 BY CITY:")
        for city_stat in sorted(stats['cities'], key=lambda x: x['places'], reverse=True):
            print(f"  {city_stat['city']}: {city_stat['places']} places ({city_stat['posts']} posts)")
        
        if places:
            # Category breakdown
            categories = {}
            for p in places:
                categories[p['category']] = categories.get(p['category'], 0) + 1
            
            print(f"\n📂 BY CATEGORY:")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat}: {count}")
            
            # Top tags
            tags = {}
            for p in places:
                for tag in p.get('tags', []):
                    tags[tag] = tags.get(tag, 0) + 1
            
            print(f"\n🏷️ TOP TAGS:")
            for tag, count in sorted(tags.items(), key=lambda x: x[1], reverse=True)[:15]:
                print(f"  {tag}: {count}")
            
            # Multi-mention places
            multi = [p for p in places if p.get('mention_count', 1) > 1]
            if multi:
                print(f"\n🔥 MOST MENTIONED ({len(multi)} places):")
                for p in sorted(multi, key=lambda x: x['mention_count'], reverse=True)[:10]:
                    print(f"  {p['name']} ({p['city']}) - {p['mention_count']}x mentions")


def harvest_single_city(city: str):
    """Convenience function to harvest one city."""
    harvester = Harvester()
    result = harvester.harvest_city(city)
    
    if result['places']:
        harvester.extractor.save_results(result['places'], f"{city.lower().replace(' ', '_')}.json")
        harvester.extractor.print_summary(result['places'])
    
    return result


def harvest_all():
    """Convenience function to harvest all target cities."""
    harvester = Harvester()
    return harvester.harvest_all_cities()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Lowkey Place Harvester")
    parser.add_argument("--city", type=str, help="Harvest single city (e.g., 'Paris')")
    parser.add_argument("--all", action="store_true", help="Harvest all target cities")
    parser.add_argument("--test", action="store_true", help="Test run with 2 cities, 2 queries each")
    
    args = parser.parse_args()
    
    if args.city:
        harvest_single_city(args.city)
    elif args.all:
        harvest_all()
    elif args.test:
        # Quick test run
        harvester = Harvester()
        harvester.harvest_all_cities(
            cities=["Paris", "Tokyo"],
        )
    else:
        # Default: harvest all
        print("Usage:")
        print("  python harvester.py --city Paris     # Single city")
        print("  python harvester.py --all            # All 10 cities")
        print("  python harvester.py --test           # Test run (2 cities)")