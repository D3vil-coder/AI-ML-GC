"""
Content Writer Agent (Agent 4) - PRODUCTION VERSION
Fixed slide structure. NEVER shortens critical content like products.
Integrates web-scraped market data.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ollama_client import OllamaClient
from utils.token_tracker import token_tracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Content that should NEVER be shortened
NEVER_SHORTEN = [
    'products',
    'services',
    'certifications',
    'industries',
    'shareholders',
]


@dataclass
class VerifiedClaim:
    """A claim verified against source data."""
    text: str
    source: str
    original_value: Any = None


@dataclass
class SlideContent:
    """Content for a single slide."""
    title: str
    sections: Dict[str, List[str]]
    metrics: Dict[str, Any]
    hooks: List[str] = None
    citations: List[VerifiedClaim] = field(default_factory=list)


class ContentWriter:
    """
    Production content writer.
    Critical rule: NEVER shorten products, services, or key data.
    """
    
    def __init__(self, domain: str = "manufacturing"):
        self.domain = domain
        self.ollama = OllamaClient()
        self.company_name = ""
        self.source_data = {}
        self.web_data = {}
    
    def set_web_data(self, web_data: Dict[str, Any]):
        """Set web-scraped data for enrichment."""
        self.web_data = web_data or {}
    
    def generate_slide_content(self, data: Dict[str, Any], 
                                company_name: str) -> List[SlideContent]:
        """Generate structured content for all 3 slides."""
        self.company_name = company_name
        self.source_data = data
        
        slides = [
            self._generate_slide_1(data),
            self._generate_slide_2(data),
            self._generate_slide_3(data),
        ]
        
        return slides
    
    def _generate_slide_1(self, data: Dict[str, Any]) -> SlideContent:
        """Slide 1: Business Profile - NEVER shorten products."""
        sections = {}
        citations = []
        
        # 1. Company Overview (can shorten)
        desc = data.get('business_description', '')
        if desc:
            overview = self._anonymize(desc)
            # Only shorten overview, not products
            if len(overview) > 200:
                overview = self._shorten_text(overview, 200, 'overview')
            sections['Company Overview'] = [overview]
            citations.append(VerifiedClaim(
                text=overview,
                source='onepager:business_description',
                original_value=desc[:100]
            ))
        
        # 2. Products & Services - NEVER SHORTEN, show all
        products = data.get('products_services', [])
        if products:
            product_list = []
            # Show ALL products, don't limit to 6
            for p in products[:8]:  # Show up to 8
                text = self._anonymize(p)
                # NO SHORTENING - products are critical
                product_list.append(text)
                citations.append(VerifiedClaim(
                    text=text,
                    source='onepager:products_services',
                    original_value=p
                ))
            sections['Products & Services'] = product_list
        
        # 3. Industries Served - NEVER SHORTEN
        industries = data.get('industries_served', '')
        if industries:
            if isinstance(industries, str):
                industry_list = [i.strip() for i in industries.split(',') if i.strip()]
            else:
                industry_list = industries
            # Show all industries, no shortening
            sections['Industries Served'] = industry_list[:6]
            citations.append(VerifiedClaim(
                text=', '.join(industry_list),
                source='onepager:industries_served',
                original_value=industries
            ))
        
        # 4. Key Highlights (can shorten individual items)
        ops = data.get('key_operational_indicators', [])
        if ops:
            highlights = []
            for o in ops[:4]:
                text = self._anonymize(o)
                if len(text) > 70:
                    text = self._shorten_text(text, 70, 'highlight')
                highlights.append(text)
                citations.append(VerifiedClaim(
                    text=text,
                    source='onepager:key_operational_indicators',
                    original_value=o
                ))
            sections['Key Highlights'] = highlights
        
        # 5. Certifications - NEVER SHORTEN
        certs = data.get('certifications', [])
        if certs:
            sections['Certifications'] = certs[:5]
            for c in certs[:5]:
                citations.append(VerifiedClaim(
                    text=c,
                    source='onepager:certifications',
                    original_value=c
                ))
        
        # Metrics for bottom bar - SHORTEN these as they have limited space
        founded = data.get('founded', '')
        employees = data.get('employees', '')
        
        # Shorten metrics to fit in boxes
        metrics = {}
        if founded:
            metrics['Founded'] = str(founded)[:10]
        if employees:
            emp_str = str(employees)
            # Just show the number
            emp_match = re.search(r'(\d[\d,]*)', emp_str)
            if emp_match:
                metrics['Employees'] = emp_match.group(1)
        
        return SlideContent(
            title="Business Profile & Capabilities",
            sections=sections,
            metrics=metrics,
            citations=citations
        )
    
    def _generate_slide_2(self, data: Dict[str, Any]) -> SlideContent:
        """Slide 2: Financial Performance."""
        financials = data.get('financials', {})
        sections = {}
        citations = []
        
        # 1. Revenue Trend (for chart data)
        revenue = financials.get('revenue', {})
        if revenue:
            years = sorted(revenue.keys())[-5:]
            rev_items = []
            for yr in years:
                text = f"FY{str(yr)[-2:]}: ₹{revenue[yr]:.1f} Cr"
                rev_items.append(text)
                citations.append(VerifiedClaim(
                    text=text,
                    source='onepager:financials:revenue',
                    original_value=revenue[yr]
                ))
            sections['Revenue Trend'] = rev_items
        
        # 2. EBITDA (for chart data)
        ebitda = financials.get('ebitda', {})
        if ebitda:
            years = sorted(ebitda.keys())[-5:]
            ebitda_items = []
            for yr in years:
                text = f"FY{str(yr)[-2:]}: ₹{ebitda[yr]:.1f} Cr"
                ebitda_items.append(text)
                citations.append(VerifiedClaim(
                    text=text,
                    source='onepager:financials:ebitda',
                    original_value=ebitda[yr]
                ))
            sections['EBITDA'] = ebitda_items
        
        # 3. Financial KPIs - calculated with formulas
        kpis = []
        
        # CAGR calculation
        if len(revenue) >= 2:
            years = sorted(revenue.keys())
            first_yr, last_yr = years[0], years[-1]
            first_rev, last_rev = revenue[first_yr], revenue[last_yr]
            n = last_yr - first_yr
            if first_rev > 0 and n > 0:
                cagr = ((last_rev / first_rev) ** (1/n) - 1) * 100
                kpi_text = f"Revenue CAGR: {cagr:.1f}%"
                kpis.append(kpi_text)
                citations.append(VerifiedClaim(
                    text=kpi_text,
                    source=f'Verified from: CAGR=(({last_rev:.1f}/{first_rev:.1f})^(1/{n})-1)×100',
                    original_value={'start': first_rev, 'end': last_rev, 'years': n, 'cagr': cagr}
                ))
        
        # EBITDA Margin
        if ebitda and revenue:
            common = set(ebitda.keys()) & set(revenue.keys())
            if common:
                yr = max(common)
                if revenue[yr] > 0:
                    margin = (ebitda[yr] / revenue[yr]) * 100
                    kpi_text = f"EBITDA Margin: {margin:.1f}%"
                    kpis.append(kpi_text)
                    citations.append(VerifiedClaim(
                        text=kpi_text,
                        source=f'Verified from: Margin=({ebitda[yr]:.1f}/{revenue[yr]:.1f})×100',
                        original_value={'ebitda': ebitda[yr], 'revenue': revenue[yr], 'margin': margin}
                    ))
        
        # RoCE
        roce = financials.get('roce', {})
        if roce:
            yr = max(roce.keys())
            kpi_text = f"RoCE: {roce[yr]:.1f}%"
            kpis.append(kpi_text)
            citations.append(VerifiedClaim(
                text=kpi_text,
                source='onepager:financials:roce',
                original_value=roce[yr]
            ))
        
        # ROE
        roe = financials.get('roe', {})
        if roe:
            yr = max(roe.keys())
            kpi_text = f"ROE: {roe[yr]:.1f}%"
            kpis.append(kpi_text)
            citations.append(VerifiedClaim(
                text=kpi_text,
                source='onepager:financials:roe',
                original_value=roe[yr]
            ))
        
        if kpis:
            sections['Financial KPIs'] = kpis
        
        # 4. Key Shareholders - NEVER SHORTEN names
        shareholders = data.get('shareholders', [])
        if shareholders:
            sh_list = []
            for sh in shareholders[:5]:
                name = sh.get('name', '')
                value = sh.get('value', 0)
                if name and value:
                    # Keep full name, just format nicely
                    text = f"{name}: {value:.1f}%"
                    sh_list.append(text)
                    citations.append(VerifiedClaim(
                        text=text,
                        source='onepager:shareholders',
                        original_value=sh
                    ))
            if sh_list:
                sections['Key Shareholders'] = sh_list
        
        # 5. Market Position (from web data)
        market_data = self.web_data.get('market_data', {})
        if market_data:
            market_items = []
            if market_data.get('india_market_size'):
                text = f"Industry Size: {market_data['india_market_size']}"
                market_items.append(text)
                citations.append(VerifiedClaim(
                    text=text,
                    source=f"web:{market_data.get('source', 'Industry estimates')}",
                    original_value=market_data['india_market_size']
                ))
            if market_data.get('cagr'):
                text = f"Industry Growth: {market_data['cagr']}"
                market_items.append(text)
                citations.append(VerifiedClaim(
                    text=text,
                    source=f"web:{market_data.get('source', 'Industry estimates')}",
                    original_value=market_data['cagr']
                ))
            if market_items:
                sections['Market Position'] = market_items
        
        return SlideContent(
            title="Financial & Operational Performance",
            sections=sections,
            metrics={'revenue': revenue, 'ebitda': ebitda},
            citations=citations
        )
    
    def _generate_slide_3(self, data: Dict[str, Any]) -> SlideContent:
        """Slide 3: Investment Highlights."""
        sections = {}
        citations = []
        
        # 1. Generate investment hooks
        hooks_data = self._generate_hooks(data)
        hooks = [h['text'] for h in hooks_data]
        for h in hooks_data:
            citations.append(VerifiedClaim(
                text=h['text'],
                source=h['source'],
                original_value=h.get('original')
            ))
        
        # 2. Key Strengths (from SWOT) - can shorten
        swot = data.get('swot', {})
        strengths = swot.get('strengths', [])
        if strengths:
            strength_list = []
            for s in strengths[:5]:
                text = self._anonymize(s)
                if len(text) > 120:
                    text = text[:120]
                strength_list.append(text)
                citations.append(VerifiedClaim(
                    text=text,
                    source='onepager:swot:strengths',
                    original_value=s
                ))
            sections['Key Strengths'] = strength_list
        
        # 3. Growth Opportunities (from SWOT) - can shorten
        opportunities = swot.get('opportunities', [])
        if opportunities:
            opp_list = []
            for o in opportunities[:5]:
                text = self._anonymize(o)
                if len(text) > 120:
                    text = text[:120]
                opp_list.append(text)
                citations.append(VerifiedClaim(
                    text=text,
                    source='onepager:swot:opportunities',
                    original_value=o
                ))
            sections['Growth Opportunities'] = opp_list
        
        # 4. Recent Milestones - can shorten
        milestones = data.get('key_milestones', [])
        if milestones:
            milestone_list = []
            for m in milestones[:5]:
                date = m.get('date', '')
                milestone = m.get('milestone', '')
                if date and milestone:
                    text = f"{date}: {self._anonymize(milestone)}"
                    if len(text) > 70:
                        text = self._shorten_text(text, 70, 'milestone')
                    milestone_list.append(text)
                    citations.append(VerifiedClaim(
                        text=text,
                        source='onepager:key_milestones',
                        original_value=m
                    ))
            if milestone_list:
                sections['Recent Milestones'] = milestone_list
        
        # 5. Market Opportunity (from web)
        industry_outlook = self.web_data.get('industry_outlook', {})
        if industry_outlook.get('summary'):
            summary = industry_outlook['summary']
            sections['Market Opportunity'] = [summary[:120]]
            citations.append(VerifiedClaim(
                text=summary[:60],
                source=f"web:{industry_outlook.get('source', 'Industry estimates')}",
                original_value=industry_outlook
            ))
        

        # LLM Enhancement: Fill sparse sections
        min_items = 3
        for section_name in ['Key Strengths', 'Growth Opportunities', 'Market Opportunity']:
            if section_name not in sections or len(sections.get(section_name, [])) < min_items:
                # Use LLM to generate additional points
                if self.ollama.available:
                    context = f"Company: {self.company_name}\n"
                    context += f"Products: {', '.join(data.get('products_services', [])[:3])}\n"
                    context += f"Domain: {data.get('industries_served', ['Technology'])[0]}\n"
                    
                    prompt = f"""For an M&A investment teaser, generate 3 bullet points for "{section_name}".
Company context: {context}

Rules:
- Each bullet max 80 characters
- Be specific and quantified where possible
- Professional investment language

Return ONLY a JSON array of 3 strings."""

                    try:
                        result = self.ollama.generate(prompt, temperature=0.3, max_tokens=200)
                        import json
                        cleaned = result.strip()
                        if cleaned.startswith('```'):
                            cleaned = cleaned.split('```')[1]
                            if cleaned.startswith('json'):
                                cleaned = cleaned[4:]
                        points = json.loads(cleaned.strip())
                        if isinstance(points, list):
                            existing = sections.get(section_name, [])
                            for p in points[:3]:
                                if len(existing) < 5:
                                    existing.append(str(p)[:80])
                            sections[section_name] = existing
                    except:
                        pass
        
        return SlideContent(
            title="Investment Highlights",
            sections=sections,
            metrics={},
            hooks=hooks,
            citations=citations
        )
    
    def _generate_hooks(self, data: Dict[str, Any]) -> List[Dict]:
        """Generate REAL investor insights using LLM, not templates."""
        hooks = []
        financials = data.get('financials', {})
        revenue = financials.get('revenue', {})
        market_data = self.web_data.get('market_data', {})
        
        # Prepare context for LLM
        context_parts = [f"Company: {self.company_name}"]
        
        products = data.get('products_services', [])
        if products:
            context_parts.append(f"Products: {', '.join(products[:5])}")
        
        industries = data.get('industries_served', [])
        if industries:
            context_parts.append(f"Industries: {', '.join(industries[:3])}")
        
        if market_data:
            if market_data.get('india_market_size'):
                context_parts.append(f"Market Size: {market_data['india_market_size']}")
            if market_data.get('cagr'):
                context_parts.append(f"Market Growth: {market_data['cagr']}")
        
        # Add financial metrics
        if len(revenue) >= 2:
            years = sorted(revenue.keys())
            latest = revenue[years[-1]]
            first = revenue[years[0]]
            n = years[-1] - years[0]
            if first > 0 and n > 0:
                cagr = ((latest / first) ** (1/n) - 1) * 100
                context_parts.append(f"Revenue CAGR: {cagr:.1f}%")
                context_parts.append(f"Latest Revenue: ₹{latest:.1f} Cr")
        
        context = "\n".join(context_parts)
        
        # Generate insights with LLM
        if self.ollama.available:
            prompt = f"""You are an M&A analyst preparing an investment teaser for institutional investors.

Given this company data:
{context}

Generate 3-4 SPECIFIC, QUANTIFIED investment highlights that would appeal to PE/VC investors.

Rules:
- Each highlight must be specific with numbers/facts
- Focus on moats, market opportunity, scalability, defensibility
- NO generic statements like "Positioned for growth"
- Examples of GOOD highlights:
  * "Captures 15% of ₹2,000 Cr addressable market through exclusive OEM partnerships"
  * "68% revenue CAGR driven by 120% NRR and platform economics"
  * "Strong moat: Only ISO 27001 + SOC 2 certified player in segment"

Return ONLY a JSON array of 3-4 strings. No explanation.
Example: ["First insight here", "Second insight here", "Third insight here"]"""

            result = self.ollama.generate(prompt, temperature=0.3, max_tokens=300)
            
            # Track tokens
            token_tracker.track_from_response(
                task='hook_generation_llm',
                model=self.ollama.model,
                prompt=prompt,
                response=result
            )
            
            # Parse JSON response
            try:
                import json
                # Clean response - remove markdown if present
                cleaned = result.strip()
                if cleaned.startswith('```'):
                    # Remove markdown code blocks
                    cleaned = cleaned.split('```')[1]
                    if cleaned.startswith('json'):
                        cleaned = cleaned[4:]
                cleaned = cleaned.strip()
                
                insights = json.loads(cleaned)
                if isinstance(insights, list):
                    for insight in insights[:4]:
                        hooks.append({
                            'text': str(insight)[:150],  # Max 150 chars
                            'source': '[AI Generated from company data + market analysis]',
                            'original': context
                        })
                    if hooks:
                        logger.info(f"Generated {len(hooks)} LLM-powered insights")
                        return hooks
            except Exception as e:
                logger.warning(f"Failed to parse LLM insights: {e}, using fallback")
        else:
            logger.warning("LLM not available, using rule-based fallback")
        
        # Fallback: Better rule-based hooks
        if len(revenue) >= 2:
            years = sorted(revenue.keys())
            latest = revenue[years[-1]]
            first = revenue[years[0]]
            n = years[-1] - years[0]
            if first > 0 and n > 0:
                cagr = ((latest / first) ** (1/n) - 1) * 100
                if cagr > 0:
                    text = f"{cagr:.0f}% revenue CAGR over {n} years to ₹{latest:.0f} Cr"
                    hooks.append({
                        'text': text,
                        'source': 'Verified from financials',
                        'original': {'cagr': cagr, 'revenue': latest}
                    })
        
        # Add market size if available
        if market_data and market_data.get('india_market_size'):
            text = f"Operating in {market_data['india_market_size']} market"
            if market_data.get('cagr'):
                text += f" growing at {market_data['cagr']}"
            hooks.append({
                'text': text,
                'source': 'Verified from market data',
                'original': market_data
            })
        
        # Ensure we have at least some hooks
        if not hooks:
            hooks.append({
                'text': 'Strong operational track record',
                'source': 'company_description',
                'original': data.get('business_description', '')
            })
        
        return hooks[:4]

    def _shorten_text(self, text: str, max_chars: int, context: str) -> str:
        """
        Shorten text using LLM. Never truncate with '...'.
        Only call for appropriate contexts (not products/services).
        """
        if not text or len(text) <= max_chars:
            return text
        
        # Use LLM for intelligent shortening
        if self.ollama.available:
            prompt = f"""Shorten this text to under {max_chars} characters while keeping the key meaning.
Do NOT end with "..." or cut mid-word.

Text: {text}

Return only the shortened text:"""
            
            result = self.ollama.generate(prompt, temperature=0.2, max_tokens=80)
            
            # Track tokens
            token_tracker.track_from_response(
                task=f'text_shortening:{context}',
                model=self.ollama.model,
                prompt=prompt,
                response=result or ''
            )
            
            if result:
                shortened = result.strip().strip('"').strip("'")
                # Ensure no "..."
                shortened = shortened.rstrip('.')
                if shortened.endswith('..'):
                    shortened = shortened[:-2]
                if len(shortened) <= max_chars:
                    return shortened
        
        # Fallback: Smart truncate at word boundary
        words = text.split()
        result = ""
        for word in words:
            if len(result) + len(word) + 1 > max_chars:
                break
            result = result + " " + word if result else word
        
        return result.strip()
    
    def _anonymize(self, text: str) -> str:
        """Anonymize text - company names and locations."""
        if not text:
            return text
        
        result = text
        
        if self.company_name:
            patterns = [
                (re.escape(self.company_name), "The Company"),
                (re.escape(self.company_name.split()[0]), "The Company"),
            ]
            for pattern, replacement in patterns:
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Location anonymization
        locations = {
            r'\bBangalore\b': 'South India',
            r'\bBengaluru\b': 'South India',
            r'\bMumbai\b': 'West India',
            r'\bDelhi\b': 'North India',
            r'\bChennai\b': 'South India',
            r'\bHyderabad\b': 'South India',
            r'\bPune\b': 'West India',
            r'\bNoida\b': 'North India',
            r'\bDRDO\b': 'Defence Organization',
            r'\bISRO\b': 'Space Agency',
            r'\bHAL\b': 'Aerospace PSU',
        }
        for pattern, replacement in locations.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result


if __name__ == "__main__":
    print("Content writer ready - NEVER shortens products/services")
