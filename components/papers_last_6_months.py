"""
Papers published in last 6 months component.
"""
from components.base_component import BaseComponent
from components.utils import get_first_author_name
import streamlit as st
import pandas as pd
import datetime


class PapersLast6MonthsComponent(BaseComponent):
    """Component for displaying papers published in the last 6 months."""
    
    def __init__(self, data: pd.DataFrame = None, **kwargs):
        """
        Initialize the papers last 6 months component.
        
        Args:
            data: Main publications DataFrame
        """
        super().__init__(data=data, **kwargs)
    
    def render(self) -> None:
        """Render the papers last 6 months component."""
        if not self.validate_data():
            st.warning("No data available to display recent papers.")
            return
        
        st.markdown('<div class="section-header">📅 Papers Published in Last 6 Months Citing AURIN</div>', unsafe_allow_html=True)
        
        # Filter papers from last 6 months
        six_months_ago = datetime.datetime.now() - datetime.timedelta(days=180)
        
        # Work with a copy to avoid mutating original data
        data_copy = self.data.copy()
        
        # Convert date column to datetime if not already
        if 'date' in data_copy.columns:
            data_copy['date'] = pd.to_datetime(data_copy['date'], errors='coerce')
        
        recent_6_months_papers = data_copy[
            data_copy['date'] >= six_months_ago
        ].sort_values(by='date', ascending=False)
        
        if not recent_6_months_papers.empty:
            st.info(f"Found {len(recent_6_months_papers)} papers published in the last 6 months (since {six_months_ago.strftime('%B %d, %Y')})")
            
            # Create base display dataframe
            recent_6m_display_df = recent_6_months_papers[['title', 'date', 'journal.title', 'times_cited']].copy()
            
            # Extract first author's name from authors column if available
            if 'authors' in recent_6_months_papers.columns:
                # Apply function to extract author names
                author_names = recent_6_months_papers['authors'].apply(get_first_author_name)
                recent_6m_display_df['first_author_name'] = author_names.apply(lambda x: x[0]+" "+x[1] if x[0] and x[1] else '')
                # Reorder columns: Title, First Author, Publication Date, Journal, Citations
                recent_6m_display_df = recent_6m_display_df[['title', 'first_author_name', 'date', 'journal.title', 'times_cited']]
                recent_6m_display_df.columns = ['Title', 'First Author', 'Publication Date', 'Journal', 'Citations']
            else:
                recent_6m_display_df.columns = ['Title', 'Publication Date', 'Journal', 'Citations']
            
            recent_6m_display_df['Publication Date'] = pd.to_datetime(recent_6m_display_df['Publication Date']).dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                recent_6m_display_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No papers found in the last 6 months.")

