"""
Data loading module for AURIN Impact Tracking Dashboard.
Provides abstract base class and concrete implementation for loading data from Dimensions API.
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple
import streamlit as st
import dimcli
import pandas as pd


class BaseDataLoader(ABC):
    """Abstract base class for data loaders."""
    
    @abstractmethod
    def load_data(self, api_key: str) -> Tuple[Optional[pd.DataFrame], ...]:
        """
        Load data from the data source.
        
        Args:
            api_key: API key for authentication
            
        Returns:
            Tuple of DataFrames (main, authors, affiliations, funders, investigators)
        """
        pass
    
    @abstractmethod
    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate the API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass


def _validate_api_key(api_key: str) -> bool:
    """
    Validate the API key.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key or not api_key.strip():
        return False
    return True


@st.cache_data
def _load_dimensions_data(api_key: str, endpoint: str, query: str) -> Tuple[Optional[pd.DataFrame], ...]:
    """
    Cached function to load and process AURIN data from Dimensions API.
    
    Args:
        api_key: Dimensions API key
        endpoint: Dimensions API endpoint
        query: Query string for fetching publications
        
    Returns:
        Tuple of DataFrames (main, authors, affiliations, funders, investigators)
    """
    try:
        if not _validate_api_key(api_key):
            st.error("Please enter your Dimensions API key in the sidebar to load data.")
            return None, None, None, None, None
        
        dimcli.login(key=api_key, endpoint=endpoint)
        dsl = dimcli.Dsl()
        
        res_aurin = dsl.query_iterative(query)
        df_aurin_main = res_aurin.as_dataframe()
        df_authors = res_aurin.as_dataframe_authors()
        df_affiliations = res_aurin.as_dataframe_authors_affiliations()
        df_funders = res_aurin.as_dataframe_funders()
        df_investigators = res_aurin.as_dataframe_investigators()
        
        # Join times_cited from df_aurin_main to df_affiliations
        # Join on pub_id (df_affiliations) and id (df_aurin_main)
        if df_affiliations is not None and not df_affiliations.empty and df_aurin_main is not None and not df_aurin_main.empty:
            if 'pub_id' in df_affiliations.columns and 'id' in df_aurin_main.columns and 'times_cited' in df_aurin_main.columns:
                # Create a subset of df_aurin_main with only id and times_cited for the join
                citation_df = df_aurin_main[['id', 'times_cited']].copy()
                # Merge times_cited into df_affiliations based on pub_id = id
                # Use suffixes to handle potential conflicts if times_cited already exists
                df_affiliations = df_affiliations.merge(
                    citation_df,
                    left_on='pub_id',
                    right_on='id',
                    how='left',
                    suffixes=('', '_from_main')
                )
                # Update times_cited column: use merged value if available, otherwise keep original
                if 'times_cited_from_main' in df_affiliations.columns:
                    df_affiliations['times_cited'] = df_affiliations['times_cited_from_main']
                    df_affiliations = df_affiliations.drop(columns=['times_cited_from_main'], errors='ignore')
                # Drop the 'id' column from citation_df that was added during merge
                if 'id' in df_affiliations.columns:
                    df_affiliations = df_affiliations.drop(columns=['id'], errors='ignore')
        
        return df_aurin_main, df_authors, df_affiliations, df_funders, df_investigators
        
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
            st.error("❌ Authentication failed. Please check your API key.")
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            st.error("❌ Connection error. Please check your internet connection.")
        else:
            st.error(f"❌ Error loading data: {error_msg}")
        return None, None, None, None, None


class DimensionsDataLoader(BaseDataLoader):
    """Concrete implementation of data loader for Dimensions API."""
    
    def __init__(self, endpoint: str = "https://app.dimensions.ai", query: str = None):
        """
        Initialize the Dimensions data loader.
        
        Args:
            endpoint: Dimensions API endpoint
            query: Query string for fetching publications
        """
        self.endpoint = endpoint
        self.query = query or """
            search publications for "\\"Australian Urban Research Infrastructure Network\\""
            return publications[id+title+authors+pages+type+volume+issue+journal+times_cited+date+date_online]
        """
    
    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate the API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid, False otherwise
        """
        return _validate_api_key(api_key)
    
    def load_data(self, api_key: str) -> Tuple[Optional[pd.DataFrame], ...]:
        """
        Load and process AURIN data from Dimensions API.
        
        Args:
            api_key: Dimensions API key
            
        Returns:
            Tuple of DataFrames (main, authors, affiliations, funders, investigators)
        """
        return _load_dimensions_data(api_key, self.endpoint, self.query)

