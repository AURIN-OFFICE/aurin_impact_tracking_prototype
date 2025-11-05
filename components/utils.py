"""
Utility functions for components.
"""
import pandas as pd


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

