"""
Data Validators
Schema validation, entity detection, and data integrity checks.
"""

import re
import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class DataValidator:
    """
    Validates extracted data for completeness and integrity.
    """
    
    # Required fields for a valid extraction
    REQUIRED_FIELDS = [
        'business_description',
        'website',
    ]
    
    # Fields that should have data for a complete profile
    RECOMMENDED_FIELDS = [
        'products_services',
        'financials',
        'shareholders',
    ]
    
    def __init__(self):
        self.company_names = []  # Names to check for leakage
    
    def validate_extraction(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate extracted company data.
        
        Args:
            data: Extracted company data dictionary
            
        Returns:
            ValidationResult with status, errors, and warnings
        """
        errors = []
        warnings = []
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            value = data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                errors.append(f"Missing required field: {field}")
        
        # Check recommended fields
        for field in self.RECOMMENDED_FIELDS:
            value = data.get(field)
            if not value:
                warnings.append(f"Missing recommended field: {field}")
            elif isinstance(value, (list, dict)) and len(value) == 0:
                warnings.append(f"Empty data for field: {field}")
        
        # Validate financials
        financials = data.get('financials', {})
        if isinstance(financials, dict):
            revenue = financials.get('revenue', {})
            if not revenue:
                errors.append("Missing revenue data in financials")
            elif len(revenue) < 3:
                warnings.append(f"Only {len(revenue)} years of revenue data")
            
            ebitda = financials.get('ebitda', {})
            if not ebitda:
                warnings.append("Missing EBITDA data")
        
        # Validate website URL
        website = data.get('website', '')
        if website and not self._is_valid_url(website):
            warnings.append(f"Invalid website URL format: {website}")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid format."""
        url_pattern = r'^https?://[\w\-]+(\.[\w\-]+)+[^\s]*$'
        return bool(re.match(url_pattern, url, re.IGNORECASE))
    
    def validate_anonymization(self, text: str, company_names: List[str]) -> Tuple[bool, List[str]]:
        """
        Check text for company name leakage.
        
        Args:
            text: Anonymized text to check
            company_names: List of company names that should not appear
            
        Returns:
            Tuple of (is_clean, list of found names)
        """
        found = []
        text_lower = text.lower()
        
        for name in company_names:
            if name.lower() in text_lower:
                found.append(name)
            
            # Also check variations
            variations = [
                name.replace(' ', ''),
                name.replace(' ', '-'),
                ''.join(word[0] for word in name.split()),  # Acronym
            ]
            for var in variations:
                if len(var) > 2 and var.lower() in text_lower:
                    found.append(var)
        
        return len(found) == 0, found
    
    def validate_financial_data(self, financials: Dict[str, Dict[int, float]]) -> ValidationResult:
        """
        Validate financial data for consistency.
        
        Args:
            financials: Financial data with metrics by year
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        revenue = financials.get('revenue', {})
        ebitda = financials.get('ebitda', {})
        
        if revenue:
            # Check for negative revenue (unusual)
            for year, value in revenue.items():
                if value < 0:
                    warnings.append(f"Negative revenue in {year}: {value}")
        
        if ebitda and revenue:
            # Check EBITDA vs revenue consistency
            for year in set(ebitda.keys()) & set(revenue.keys()):
                if revenue[year] > 0:
                    margin = (ebitda[year] / revenue[year]) * 100
                    if margin > 80:
                        warnings.append(f"Unusually high EBITDA margin in {year}: {margin:.1f}%")
                    elif margin < -50:
                        warnings.append(f"Very low EBITDA margin in {year}: {margin:.1f}%")
        
        pat_margin = financials.get('pat_margin', {})
        if pat_margin:
            for year, margin in pat_margin.items():
                if margin > 50:
                    warnings.append(f"Unusually high PAT margin in {year}: {margin:.1f}%")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)


def verify_citation(claim: str, source_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Verify if a claim can be traced to source data.
    
    Args:
        claim: The claim text to verify
        source_data: Source data (extracted from MD or scraped)
        
    Returns:
        Tuple of (is_verified, source_reference)
    """
    claim_lower = claim.lower()
    
    # Extract numbers from claim
    numbers = re.findall(r'[\d,]+\.?\d*', claim)
    
    # Check financials
    financials = source_data.get('financials', {})
    for metric_name, values in financials.items():
        if isinstance(values, dict):
            for year, value in values.items():
                value_str = f"{value:.2f}".rstrip('0').rstrip('.')
                if value_str in claim or str(int(value)) in numbers:
                    return True, f"Financial data: {metric_name} {year}"
    
    # Check in text sections
    text_fields = ['business_description', 'industries_served', 'headquarters']
    for field in text_fields:
        field_value = source_data.get(field, '')
        if isinstance(field_value, str) and field_value:
            # Check for significant overlap
            field_words = set(field_value.lower().split())
            claim_words = set(claim_lower.split())
            overlap = len(field_words & claim_words)
            if overlap > 3:
                return True, f"Data field: {field}"
    
    # Check in lists
    list_fields = ['products_services', 'certifications', 'awards']
    for field in list_fields:
        items = source_data.get(field, [])
        for item in items:
            if isinstance(item, str) and item.lower() in claim_lower:
                return True, f"List item from: {field}"
    
    return False, None


def extract_numbers_from_text(text: str) -> List[Tuple[str, float]]:
    """
    Extract all numerical values from text with context.
    
    Args:
        text: Input text
        
    Returns:
        List of (context, value) tuples
    """
    results = []
    
    # Pattern for numbers with context
    patterns = [
        (r'([\d,]+\.?\d*)\s*%', 'percentage'),
        (r'₹\s*([\d,]+\.?\d*)\s*(Cr|crore|Lakh|lakh|M|million|B|billion)?', 'currency'),
        (r'([\d,]+)\s*(employees?|customers?|facilities?|years?)', 'count'),
        (r'FY\s*(\d{2,4})', 'fiscal_year'),
    ]
    
    for pattern, ptype in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value_str = match.group(1).replace(',', '')
            try:
                value = float(value_str)
                context = match.group(0)
                results.append((context, value))
            except ValueError:
                continue
    
    return results


# Test
if __name__ == "__main__":
    validator = DataValidator()
    
    # Test validation
    test_data = {
        'business_description': 'A technology company',
        'website': 'https://example.com',
        'products_services': ['Software', 'Consulting'],
        'financials': {
            'revenue': {2023: 100, 2024: 120, 2025: 150},
            'ebitda': {2023: 20, 2024: 25, 2025: 35},
        }
    }
    
    result = validator.validate_extraction(test_data)
    print(f"Validation: {'PASSED' if result.is_valid else 'FAILED'}")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
    
    # Test anonymization check
    is_clean, found = validator.validate_anonymization(
        "The Company is a leader in technology",
        ["Centum Electronics", "Test Corp"]
    )
    print(f"\nAnonymization check: {'CLEAN' if is_clean else 'LEAKED'}")
    
    # Test citation verification
    verified, source = verify_citation(
        "Revenue grew to 150 Cr in FY25",
        test_data
    )
    print(f"\nCitation verified: {verified}, source: {source}")
