"""
Ollama Client Utility
Wrapper for phi4-mini model interactions.
"""

import json
import re
import logging
from typing import Dict, Any, Optional, Tuple, List

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Client for interacting with Ollama LLM (phi4-mini).
    Provides methods for domain classification, anonymization, and hook generation.
    """
    
    def __init__(self, model: str = "phi4-mini:latest"):
        self.model = model
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Ollama is available with the specified model."""
        if not OLLAMA_AVAILABLE:
            logger.warning("Ollama package not installed")
            return False
        
        try:
            models_response = ollama.list()
            
            # Handle different response formats
            if hasattr(models_response, 'models'):
                models = models_response.models
                model_names = [str(m.model) if hasattr(m, 'model') else str(m) for m in models]
            elif isinstance(models_response, dict):
                models = models_response.get('models', [])
                model_names = [m.get('name', '') if isinstance(m, dict) else str(m) for m in models]
            else:
                model_names = []
            
            # Check if our model is in the list
            available = any(self.model in name or name in self.model for name in model_names)
            
            if available:
                logger.info(f"Ollama model {self.model} ready")
            else:
                logger.warning(f"Model {self.model} not found. Available: {model_names}")
                logger.warning(f"Run: ollama pull {self.model}")
            return available
        except Exception as e:
            logger.warning(f"Ollama unavailable: {e}")
            return False
    
    def generate(self, prompt: str, temperature: float = 0.3, 
                 max_tokens: int = 500) -> Optional[str]:
        """
        Generate text using the LLM.
        
        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text or None if failed
        """
        if not self.available:
            logger.error("Ollama not available")
            return None
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": temperature,
                    "top_p": 0.9,
                    "num_predict": max_tokens
                }
            )
            return response.get('response', '').strip()
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None
    
    def anonymize_text(self, text: str, company_name: str) -> str:
        """
        Anonymize text by removing company-identifying information.
        
        Args:
            text: Original text to anonymize
            company_name: Company name to replace
            
        Returns:
            Anonymized text
        """
        if not self.available:
            # Fallback: simple regex replacement
            return self._simple_anonymize(text, company_name)
        
        prompt = f"""You are an M&A anonymization expert.

Rewrite the following text to remove all company-identifying information:
- Replace "{company_name}" with "The Company" or "The Target"
- Replace specific location names with generic regions ("Northern India", "Metropolitan area")
- Keep all numbers, percentages, and metrics EXACTLY as stated
- Maintain professional M&A investment memo tone

DO NOT change any financial data. DO NOT add information not present.

Original Text:
{text}

Anonymized Text:"""

        result = self.generate(prompt, temperature=0.2, max_tokens=len(text) + 200)
        
        if result:
            # Verify company name is removed
            if company_name.lower() in result.lower():
                result = self._simple_anonymize(result, company_name)
            return result
        
        return self._simple_anonymize(text, company_name)
    
    def _simple_anonymize(self, text: str, company_name: str) -> str:
        """Simple regex-based anonymization fallback."""
        # Replace company name variations
        replacements = [
            (company_name, "The Company"),
            (company_name.upper(), "THE COMPANY"),
            (company_name.lower(), "the company"),
            (company_name.replace(" ", "-"), "The-Company"),
            (company_name.replace(" ", ""), "TheCompany"),
        ]
        
        result = text
        for old, new in replacements:
            result = result.replace(old, new)
        
        # Replace common location patterns
        location_patterns = [
            (r'\b(Bangalore|Bengaluru)\b', 'a major technology hub'),
            (r'\b(Mumbai|Delhi|Chennai|Hyderabad|Kolkata|Pune)\b', 'a metropolitan city'),
            (r'\bIndia\b', 'the region'),
        ]
        
        for pattern, replacement in location_patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def generate_investment_hooks(self, domain: str, 
                                   key_metrics: Dict[str, Any]) -> List[str]:
        """
        Generate investment highlight statements.
        
        Args:
            domain: Company domain (manufacturing, technology, etc.)
            key_metrics: Key financial/operational metrics
            
        Returns:
            List of 3 investment hook statements
        """
        if not self.available:
            return self._generate_default_hooks(domain, key_metrics)
        
        metrics_str = json.dumps(key_metrics, indent=2, default=str)
        
        prompt = f"""You are an M&A investment banker writing investment hooks.

Domain: {domain}
Key Metrics: {metrics_str}

Generate 3 compelling investment highlight statements for this company.
Each statement should be:
- One sentence, max 15 words
- Quantitative where possible (use actual numbers from metrics)
- Focused on competitive advantage or growth
- Professional M&A tone

Format as JSON array of strings.
Example: ["Industry-leading margins with 25%+ EBITDA", "Diversified revenue across 8 end-user industries"]

Your response (JSON array only):"""

        result = self.generate(prompt, temperature=0.4, max_tokens=300)
        
        if result:
            try:
                # Try to extract JSON array
                json_match = re.search(r'\[.*?\]', result, re.DOTALL)
                if json_match:
                    hooks = json.loads(json_match.group())
                    if isinstance(hooks, list) and len(hooks) >= 3:
                        return hooks[:3]
            except json.JSONDecodeError:
                pass
        
        return self._generate_default_hooks(domain, key_metrics)
    
    def _generate_default_hooks(self, domain: str, 
                                 metrics: Dict[str, Any]) -> List[str]:
        """Generate default investment hooks based on domain."""
        hooks = []
        
        # Try to generate data-driven hooks
        if 'revenue_cagr' in metrics:
            hooks.append(f"Strong revenue growth with {metrics['revenue_cagr']:.1f}% CAGR")
        
        if 'ebitda_margin' in metrics:
            hooks.append(f"Healthy profitability with {metrics['ebitda_margin']:.1f}% EBITDA margin")
        
        if 'customer_count' in metrics:
            hooks.append(f"Diversified customer base of {metrics['customer_count']}+ clients")
        
        # Domain-specific defaults
        domain_hooks = {
            'manufacturing': [
                "Established manufacturing infrastructure with proven capabilities",
                "Strong operational track record in mission-critical segments",
                "Multiple growth levers across end-user industries"
            ],
            'technology': [
                "Scalable technology platform with strong IP",
                "High-margin recurring revenue model",
                "Strategic partnerships with global technology leaders"
            ],
            'logistics': [
                "Pan-India network with strategic hub locations",
                "Technology-enabled logistics platform",
                "Strong presence in high-growth e-commerce segment"
            ],
            'consumer': [
                "Strong brand equity in growing consumer segment",
                "Multi-channel presence with D2C focus",
                "Attractive unit economics with strong repeat rates"
            ],
            'healthcare': [
                "Diversified therapeutic portfolio with regulatory approvals",
                "Strong R&D pipeline with multiple products",
                "Export presence in regulated markets"
            ],
            'infrastructure': [
                "Strong order book providing revenue visibility",
                "Proven track record of timely project execution",
                "Strategic relationships with government clients"
            ],
            'chemicals': [
                "Proprietary formulations with high entry barriers",
                "Diversified end-user industry exposure",
                "Strong export contribution with global presence"
            ],
            'automotive': [
                "Long-standing OEM relationships with tier-1 customers",
                "Technical capabilities in precision components",
                "Positioned to benefit from industry growth trends"
            ]
        }
        
        default = domain_hooks.get(domain, domain_hooks['manufacturing'])
        
        # Fill remaining slots with defaults
        while len(hooks) < 3:
            if default:
                hooks.append(default.pop(0))
            else:
                break
        
        return hooks[:3]
    
    def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        """Extract key bullet points from text."""
        if not self.available:
            # Simple extraction: split by sentences, take first N
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences[:num_points] if s.strip()]
        
        prompt = f"""Extract the {num_points} most important points from this text as bullet points.
Each point should be concise (under 15 words).

Text:
{text[:1500]}

Return as a JSON array of strings:"""

        result = self.generate(prompt, temperature=0.2, max_tokens=300)
        
        if result:
            try:
                json_match = re.search(r'\[.*?\]', result, re.DOTALL)
                if json_match:
                    points = json.loads(json_match.group())
                    if isinstance(points, list):
                        return points[:num_points]
            except json.JSONDecodeError:
                pass
        
        # Fallback
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences[:num_points] if s.strip()]


# Test
if __name__ == "__main__":
    client = OllamaClient()
    
    print(f"Ollama available: {client.available}")
    
    if client.available:
        # Test anonymization
        test_text = "Centum Electronics has facilities in Bangalore and exports to Europe."
        anonymized = client.anonymize_text(test_text, "Centum Electronics")
        print(f"\nOriginal: {test_text}")
        print(f"Anonymized: {anonymized}")
        
        # Test hooks
        metrics = {
            'revenue_cagr': 12.5,
            'ebitda_margin': 8.5,
            'customer_count': 50
        }
        hooks = client.generate_investment_hooks('manufacturing', metrics)
        print(f"\nInvestment Hooks:")
        for hook in hooks:
            print(f"  - {hook}")
    else:
        print("\nOllama not available. To enable:")
        print("  1. Install Ollama: https://ollama.com/download")
        print("  2. Run: ollama pull phi4-mini")
        print("  3. Start Ollama service")
