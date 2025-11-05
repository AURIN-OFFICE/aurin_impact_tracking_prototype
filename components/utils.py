"""
Utility functions for components.
"""
import pandas as pd
try:
    import pycountry
    PYCOUNTRY_AVAILABLE = True
except ImportError:
    PYCOUNTRY_AVAILABLE = False


def get_first_author_name(authors):
    """
    Extract first author's first_name and last_name from authors column.
    
    Args:
        authors: Authors data (typically a list of dictionaries)
        
    Returns:
        Tuple of (first_name, last_name) or (None, None) if not available
    """
    # Check for None or NaN (scalar values only)
    if authors is None:
        return None, None
    
    # Check for NaN - only for scalar values to avoid array ambiguity
    try:
        if isinstance(authors, float) and pd.isna(authors):
            return None, None
    except (TypeError, ValueError):
        pass
    
    # Check if it's a list and not empty
    if not isinstance(authors, list):
        return None, None
    
    if len(authors) == 0:
        return None, None
    
    try:
        # Get first author from list
        first_author = authors[0]
        if isinstance(first_author, dict):
            first_name = first_author.get('first_name', '')
            last_name = first_author.get('last_name', '')
            return first_name, last_name
    except (TypeError, AttributeError, IndexError):
        pass
    return None, None


def get_country_code(country_name):
    """
    Convert country name to ISO-3 code.
    
    Args:
        country_name: Name of the country
        
    Returns:
        ISO-3 country code (str) or None if not found
    """
    if not PYCOUNTRY_AVAILABLE:
        return None
    
    try:
        # Try exact match first
        country = pycountry.countries.search_fuzzy(country_name)[0]
        return country.alpha_3
    except (LookupError, IndexError):
        # Try common name variations
        try:
            country = pycountry.countries.get(name=country_name)
            return country.alpha_3
        except (LookupError, AttributeError):
            return None

