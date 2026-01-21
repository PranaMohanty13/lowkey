"""Gemini-based validation for Reddit posts."""
import os
from typing import Dict
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


class GeminiValidator:
    """Fast validation using Gemini Flash."""
    
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=API_KEY)
        self.model = model
    
    def validate_post(self, post_data: Dict) -> Dict:
        """Quick check if post contains specific place recommendations."""
        
        prompt = self._build_prompt(post_data)
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            result = response.text.strip().lower()
            has_recs = "yes" in result and "no" not in result.split("yes")[0]
            
            return {
                'has_recommendations': has_recs,
                'raw_response': response.text.strip()
            }
            
        except Exception as e:
            print(f"   ⚠️ Validation error: {e}")
            return {
                'has_recommendations': True,  # Default to true on error
                'raw_response': str(e)
            }
    
    def _build_prompt(self, post_data: Dict) -> str:
        """Build concise validation prompt."""
        
        title = post_data.get('title', '')
        body = (post_data.get('body') or '')[:500]
        
        comments = post_data.get('comments', [])
        top_comments = sorted(
            comments,
            key=lambda c: c.get('upvotes', 0),
            reverse=True
        )[:5]
        
        comments_text = '\n'.join([
            f"- {c.get('body', '')[:200]}"
            for c in top_comments
        ])
        
        return f"""Does this Reddit post contain specific named place recommendations (cafes, restaurants, bars, shops, attractions)?

Post Title: {title}
Post Body: {body}

Top Comments:
{comments_text}

Answer ONLY: Yes or No
Be strict: Only "Yes" if actual named places are mentioned (not just "a cafe" or "some restaurant")."""