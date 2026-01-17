"""
Dynamic Pricing Fetcher
Fetches real-time model pricing from providers on first run
"""

import json
import os
from typing import Dict, Any
from datetime import datetime


class PricingFetcher:
    """
    Fetches and caches model pricing from multiple sources.
    Falls back to static config if fetching fails.
    """
    
    # Portkey pricing endpoint (if available)
    PORTKEY_PRICING_URL = "https://api.portkey.ai/v1/pricing"
    
    # Static fallback pricing (from config.py)
    FALLBACK_PRICING = {
        "gpt-4o": {"input_cost": 0.0025, "output_cost": 0.01},
        "gpt-4o-mini": {"input_cost": 0.00015, "output_cost": 0.0006},
        "claude-sonnet-4": {"input_cost": 0.003, "output_cost": 0.015},
        "claude-haiku": {"input_cost": 0.00025, "output_cost": 0.00125},
        "claude-sonnet-4-5": {"input_cost": 0.003, "output_cost": 0.015},
    }
    
    def __init__(self, cache_file: str = "data/pricing_cache.json"):
        """Initialize pricing fetcher with cache file path."""
        self.cache_file = cache_file
        self.pricing_data = {}
        self._load_cache()
    
    def _load_cache(self):
        """Load cached pricing data if available and recent (< 24 hours)."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                
                # Check if cache is recent (< 24 hours)
                cached_time = datetime.fromisoformat(cache.get('timestamp', '2000-01-01'))
                age_hours = (datetime.now() - cached_time).total_seconds() / 3600
                
                if age_hours < 24:
                    self.pricing_data = cache.get('pricing', {})
                    print(f"✅ Loaded cached pricing (age: {age_hours:.1f}h)")
                    return True
                else:
                    print(f"⚠️  Pricing cache expired (age: {age_hours:.1f}h)")
            except Exception as e:
                print(f"⚠️  Failed to load cache: {e}")
        
        return False
    
    def _save_cache(self):
        """Save pricing data to cache file."""
        try:
            os.makedirs(os.path.dirname(self.cache_file) or '.', exist_ok=True)
            cache = {
                'timestamp': datetime.now().isoformat(),
                'pricing': self.pricing_data
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
            print(f"💾 Saved pricing cache to {self.cache_file}")
        except Exception as e:
            print(f"⚠️  Failed to save cache: {e}")
    
    def fetch_pricing(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetch pricing data (cached or live).
        
        Args:
            force_refresh: Force fetching new data even if cache exists
        
        Returns:
            Dictionary of model pricing
        """
        # Use cache if available and not forcing refresh
        if self.pricing_data and not force_refresh:
            return self.pricing_data
        
        print("\n🌐 Fetching latest model pricing...")
        
        # Try fetching from Portkey API first
        success = self._fetch_from_portkey()
        
        # If Portkey fails, try scraping provider websites
        if not success:
            print("⚠️  Portkey pricing unavailable, trying provider sources...")
            success = self._fetch_from_providers()
        
        # Fall back to static pricing if all else fails
        if not success:
            print("⚠️  Dynamic pricing unavailable, using static fallback")
            self.pricing_data = self.FALLBACK_PRICING
        
        # Save to cache
        if self.pricing_data:
            self._save_cache()
        
        return self.pricing_data
    
    def _fetch_from_portkey(self) -> bool:
        """
        Fetch pricing from Portkey API.
        (Portkey might have an endpoint that returns pricing for all models)
        """
        try:
            import requests
            
            # Note: This is a hypothetical endpoint - Portkey may not have this
            # You'd need to check Portkey docs for actual pricing API
            response = requests.get(
                self.PORTKEY_PRICING_URL,
                headers={"Authorization": f"Bearer {os.getenv('PORTKEY_API_KEY')}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Parse pricing data from response
                # Format would depend on Portkey's API structure
                self.pricing_data = self._parse_portkey_response(data)
                print("✅ Fetched pricing from Portkey API")
                return True
        except Exception as e:
            print(f"⚠️  Portkey API fetch failed: {e}")
        
        return False
    
    def _fetch_from_providers(self) -> bool:
        """
        Fetch pricing from individual providers.
        This would involve scraping or using provider APIs.
        """
        try:
            # OpenAI pricing
            openai_pricing = self._fetch_openai_pricing()
            
            # Anthropic pricing
            anthropic_pricing = self._fetch_anthropic_pricing()
            
            # Merge all pricing data
            self.pricing_data = {**openai_pricing, **anthropic_pricing}
            
            if self.pricing_data:
                print(f"✅ Fetched pricing for {len(self.pricing_data)} models")
                return True
        except Exception as e:
            print(f"⚠️  Provider fetch failed: {e}")
        
        return False
    
    def _fetch_openai_pricing(self) -> Dict[str, Any]:
        """
        Fetch OpenAI pricing.
        NOTE: OpenAI doesn't have a public pricing API, so we'd need to:
        1. Scrape their pricing page, OR
        2. Use a third-party pricing database, OR
        3. Keep static fallback
        """
        # For now, return empty - would need web scraping
        # In production, you could use BeautifulSoup to scrape openai.com/api/pricing
        return {}
    
    def _fetch_anthropic_pricing(self) -> Dict[str, Any]:
        """
        Fetch Anthropic pricing.
        Similar to OpenAI - no public API for pricing.
        """
        # For now, return empty - would need web scraping
        return {}
    
    def _parse_portkey_response(self, data: Dict) -> Dict[str, Any]:
        """Parse Portkey API response into our pricing format."""
        # This would depend on Portkey's actual response structure
        # Placeholder implementation
        pricing = {}
        
        for model in data.get('models', []):
            model_name = model.get('name', '').lower()
            pricing[model_name] = {
                'input_cost': model.get('input_price_per_1k', 0),
                'output_cost': model.get('output_price_per_1k', 0)
            }
        
        return pricing
    
    def get_model_pricing(self, model_name: str) -> Dict[str, float]:
        """
        Get pricing for a specific model.
        
        Args:
            model_name: Name of the model
        
        Returns:
            Dict with input_cost and output_cost
        """
        if not self.pricing_data:
            self.fetch_pricing()
        
        return self.pricing_data.get(model_name, self.FALLBACK_PRICING.get(model_name, {
            'input_cost': 0.001,
            'output_cost': 0.003
        }))


# Singleton instance
_pricing_fetcher = None

def get_pricing_fetcher() -> PricingFetcher:
    """Get or create the global pricing fetcher instance."""
    global _pricing_fetcher
    if _pricing_fetcher is None:
        _pricing_fetcher = PricingFetcher()
    return _pricing_fetcher


# Example usage
if __name__ == "__main__":
    fetcher = PricingFetcher()
    
    print("="*70)
    print("PRICING FETCHER TEST")
    print("="*70)
    
    # Fetch pricing (will use cache if available)
    pricing = fetcher.fetch_pricing()
    
    print(f"\n📊 Pricing data for {len(pricing)} models:")
    for model, prices in pricing.items():
        print(f"\n{model}:")
        print(f"  Input:  ${prices['input_cost']:.6f} per 1K tokens")
        print(f"  Output: ${prices['output_cost']:.6f} per 1K tokens")
    
    # Test specific model lookup
    print("\n🔍 Testing model lookup:")
    gpt4o = fetcher.get_model_pricing('gpt-4o')
    print(f"GPT-4o: {gpt4o}")
