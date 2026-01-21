"""Extract places from Reddit posts with rich vibes and tags."""
import os
import json
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


class PlaceExtractor:
    """Extract structured place data from Reddit posts with Gen Z vibes."""
    
    VALID_CATEGORIES = [
        'cafe', 'restaurant', 'bar', 'shop', 'museum', 'park', 
        'hotel', 'hostel', 'activity', 'neighborhood', 'market', 
        'street_food', 'club', 'viewpoint', 'temple', 'beach',
        'spa', 'gallery', 'theater', 'landmark'
    ]
    
    VALID_TAGS = [
        'food', 'coffee', 'drinks', 'nightlife', 'cultural', 'local', 
        'hidden_gem', 'budget', 'splurge', 'romantic', 'solo', 
        'instagram', 'views', 'chill', 'lively', 'historic',
        'art', 'nature', 'shopping', 'late_night', 'breakfast',
        'lunch', 'dinner', 'dessert', 'vegetarian', 'vegan',
        'family', 'outdoor', 'indoor', 'rooftop', 'waterfront',
        'trendy', 'traditional', 'authentic', 'touristy_but_worth_it'
    ]
    
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=API_KEY)
        self.model = model
        self.output_dir = Path(__file__).parent / "data" / "extracted_places"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._places_index: Dict[str, Dict] = {}
    
    def extract_from_post(self, post_data: Dict) -> List[Dict[str, Any]]:
        """Extract places from a single post."""
        
        prompt = self._build_prompt(post_data)
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return self._parse_response(response.text, post_data)
        except Exception as e:
            print(f"      ⚠️ Extraction error: {e}")
            return []
    
    def _build_prompt(self, post_data: Dict) -> str:
        """Build extraction prompt with Gen Z vibe instructions."""
        
        title = post_data.get('title', '')
        body = (post_data.get('body') or '')[:2000]
        
        comments = post_data.get('comments', [])
        top_comments = sorted(
            comments,
            key=lambda c: c.get('upvotes', 0),
            reverse=True
        )[:20]
        
        comments_text = '\n'.join([
            f"- {c.get('body', '')[:500]}"
            for c in top_comments
        ])
        
        categories_str = ' | '.join(self.VALID_CATEGORIES)
        tags_str = ', '.join(self.VALID_TAGS)
        
        return f"""You're a travel curator for "Lowkey" - a Gen Z app for finding authentic local spots, hidden gems, and places tourists don't know about.

Extract EVERY real place mentioned in this Reddit thread. We want cafes, restaurants, bars, shops, markets, neighborhoods, viewpoints, hotels - anything a traveler would want to visit.

---

POST TITLE: {title}

POST BODY:
{body}

REDDIT COMMENTS (sorted by upvotes):
{comments_text}

---

For EACH place, provide:
1. NAME: Exact place name (as locals call it)
2. CITY: City name
3. COUNTRY: Country name
4. CATEGORY: One of: {categories_str}
5. TAGS: 2-4 tags from: {tags_str}
6. VIBE: 2-3 sentences that capture:
   - What makes it special (why Redditors recommend it)
   - The vibe/atmosphere (cozy, chaotic, romantic, gritty, polished)
   - Pro tips (when to go, what to order, what to skip)
   - Write like you're texting a friend, not a travel guide
7. CONFIDENCE: high | medium

---

VIBE EXAMPLES (match this energy):

✅ GOOD:
"Tiny ramen counter with 8 seats where the chef's been perfecting tonkotsu for 30 years. Cash only, expect a queue, but that broth is life-changing. Go solo, sit at the counter, order the special."

"Chaotic night market that comes alive after 10pm. Follow the smoke and longest queues - locals know what's good. Budget like $5 for a full meal. Skip the touristy front stalls."

"Rooftop cocktail bar with insane sunset views over the old city. Pricey but worth it for the gram. Arrive by 5pm to snag a good spot, dress smart casual."

"Hole-in-the-wall coffee shop run by a third-gen family. The espresso hits different and they roast their own beans. Morning crowd is all locals reading newspapers."

❌ BAD (avoid this energy):
"A popular restaurant known for traditional cuisine" (Wikipedia vibes)
"Must-visit destination for tourists" (generic guidebook)
"Offers a variety of local dishes" (says nothing)

---

RULES:
- Extract ALL specific named places (even if briefly mentioned)
- Skip generic mentions ("a cafe nearby", "some bar")
- Skip major chains (Starbucks, McDonald's) unless specifically praised as exceptional
- If a place is mentioned multiple times or upvoted, it's probably good
- When in doubt about city/country, make educated guess from context
- One place per line
- Format exactly: NAME | CITY | COUNTRY | CATEGORY | TAGS | VIBE | CONFIDENCE

OUTPUT:"""
    
    def _parse_response(self, response_text: str, post_data: Dict) -> List[Dict]:
        """Parse Gemini response into structured places."""
        
        places = []
        
        for line in response_text.strip().split('\n'):
            line = line.strip()
            if not line or '|' not in line:
                continue
            
            # Skip header lines or examples
            if line.startswith('NAME') or line.startswith('---') or line.startswith('✅') or line.startswith('❌'):
                continue
            
            try:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) < 7:
                    continue
                
                name = parts[0].strip()
                city = parts[1].strip()
                country = parts[2].strip()
                category = parts[3].strip().lower().replace(' ', '_')
                tags_raw = parts[4].strip()
                vibe = parts[5].strip()
                confidence = parts[6].strip().lower()
                
                # Skip low quality
                if confidence == 'low' or len(vibe) < 20 or len(name) < 2:
                    continue
                
                # Normalize category
                if category not in self.VALID_CATEGORIES:
                    category_map = {
                        'restaurants': 'restaurant', 'bars': 'bar', 'cafes': 'cafe',
                        'coffee_shop': 'cafe', 'coffee': 'cafe', 'food_stall': 'street_food',
                        'night_market': 'market', 'shrine': 'temple', 'district': 'neighborhood',
                        'area': 'neighborhood', 'attraction': 'landmark', 'sight': 'landmark',
                        'pub': 'bar', 'lounge': 'bar', 'bistro': 'restaurant',
                    }
                    category = category_map.get(category, 'activity')
                
                # Parse and validate tags
                tags = [t.strip().lower().replace(' ', '_') for t in tags_raw.split(',')]
                tags = [t for t in tags if t in self.VALID_TAGS][:4]
                
                # Add default tags based on category if none matched
                if not tags:
                    category_to_tags = {
                        'cafe': ['coffee', 'chill'],
                        'restaurant': ['food', 'local'],
                        'bar': ['drinks', 'nightlife'],
                        'club': ['nightlife', 'lively'],
                        'street_food': ['food', 'budget', 'local'],
                        'market': ['shopping', 'local'],
                        'temple': ['cultural', 'historic'],
                        'museum': ['cultural', 'indoor'],
                        'park': ['nature', 'outdoor'],
                        'viewpoint': ['views', 'instagram'],
                        'neighborhood': ['local', 'authentic'],
                        'beach': ['outdoor', 'chill'],
                    }
                    tags = category_to_tags.get(category, ['local'])
                
                place = {
                    'name': name,
                    'city': city,
                    'country': country,
                    'category': category,
                    'tags': tags,
                    'vibe': vibe,
                    'confidence': confidence,
                    'sources': [{
                        'url': post_data.get('url', ''),
                        'title': post_data.get('title', ''),
                        'subreddit': post_data.get('subreddit', ''),
                    }],
                    'mention_count': 1
                }
                
                places.append(place)
                
            except Exception as e:
                continue
        
        return places
    
    def extract_from_posts(self, posts: List[Dict]) -> List[Dict]:
        """Extract from multiple posts with deduplication."""
        
        self._places_index = {}
        
        for i, post in enumerate(posts, 1):
            title = post.get('title', '')[:60]
            print(f"   [{i}/{len(posts)}] {title}")
            
            places = self.extract_from_post(post)
            
            if places:
                print(f"      ✅ Extracted {len(places)} places")
                for place in places:
                    self._merge_place(place)
            else:
                print(f"      ⚠️ No places extracted")
        
        return list(self._places_index.values())
    
    def _merge_place(self, new_place: Dict):
        """Merge place into index, combining vibes from duplicates."""
        
        # Create normalized key for matching
        name_normalized = new_place['name'].lower().strip()
        city_normalized = new_place['city'].lower().strip()
        key = f"{name_normalized}_{city_normalized}"
        
        if key in self._places_index:
            existing = self._places_index[key]
            
            # Merge vibes (append if different and not too long)
            new_vibe = new_place['vibe']
            if new_vibe.lower() not in existing['vibe'].lower():
                if len(existing['vibe']) < 400:
                    existing['vibe'] = f"{existing['vibe']} {new_vibe}"
                elif len(new_vibe) > len(existing['vibe']):
                    # Replace if new one is more detailed
                    existing['vibe'] = new_vibe
            
            # Merge tags (keep unique, max 6)
            existing['tags'] = list(set(existing['tags'] + new_place['tags']))[:6]
            
            # Add source
            existing['sources'].extend(new_place['sources'])
            existing['mention_count'] += 1
            
            # Boost confidence if mentioned multiple times
            if existing['mention_count'] >= 2:
                existing['confidence'] = 'high'
        else:
            self._places_index[key] = new_place
    
    def save_results(self, places: List[Dict], filename: str = "extracted_places.json"):
        """Save extracted places to JSON."""
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(places, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved {len(places)} places to: {filepath}")
        return filepath
    
    def print_summary(self, places: List[Dict]):
        """Print extraction summary."""
        
        if not places:
            print("\n❌ No places extracted")
            return
        
        print(f"\n{'='*60}")
        print(f"📊 EXTRACTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total unique places: {len(places)}")
        
        # By category
        categories = {}
        for p in places:
            categories[p['category']] = categories.get(p['category'], 0) + 1
        
        print(f"\nBy category:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")
        
        # By city
        cities = {}
        for p in places:
            city_key = f"{p['city']}, {p['country']}"
            cities[city_key] = cities.get(city_key, 0) + 1
        
        print(f"\nBy city:")
        for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:15]:
            print(f"  {city}: {count}")
        
        # Top tags
        tags = {}
        for p in places:
            for tag in p.get('tags', []):
                tags[tag] = tags.get(tag, 0) + 1
        
        print(f"\nTop tags:")
        for tag, count in sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {tag}: {count}")
        
        # Multi-mention (most validated)
        multi = [p for p in places if p.get('mention_count', 1) > 1]
        if multi:
            print(f"\n🔥 Mentioned multiple times ({len(multi)}):")
            for p in sorted(multi, key=lambda x: x['mention_count'], reverse=True)[:5]:
                print(f"  {p['name']} ({p['city']}) - {p['mention_count']}x")
        
        # Sample places
        print(f"\n📍 Sample places:")
        for place in places[:3]:
            print(f"\n  • {place['name']} ({place['city']}, {place['country']})")
            print(f"    Category: {place['category']} | Tags: {', '.join(place['tags'])}")
            vibe_preview = place['vibe'][:150] + "..." if len(place['vibe']) > 150 else place['vibe']
            print(f"    Vibe: {vibe_preview}")
            print(f"    Sources: {place['mention_count']} | Confidence: {place['confidence']}")


if __name__ == "__main__":
    # Test with sample post
    extractor = PlaceExtractor()
    
    test_post = {
        'title': 'Best cafes in Tokyo?',
        'url': 'https://reddit.com/r/JapanTravel/test',
        'subreddit': 'JapanTravel',
        'body': 'Looking for cozy coffee spots in Tokyo.',
        'num_comments': 50,
        'comments': [
            {'body': 'Onibus Coffee in Nakameguro is amazing. Tiny spot, incredible pour-over. Go early to avoid crowds.', 'upvotes': 45},
            {'body': 'Fuglen Tokyo - Norwegian coffee shop that turns into a cocktail bar at night. Very cool vibe.', 'upvotes': 32},
            {'body': 'Blue Bottle is everywhere now but their Kiyosumi shop is beautiful architecture.', 'upvotes': 28},
        ]
    }
    
    places = extractor.extract_from_post(test_post)
    
    if places:
        extractor.save_results(places, "test_extraction.json")
        extractor.print_summary(places)