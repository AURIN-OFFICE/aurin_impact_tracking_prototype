"""
Citation distribution component for visualizing citation patterns.
"""
from components.base_component import BaseComponent
import streamlit as st
import plotly.express as px


class CitationDistributionComponent(BaseComponent):
    """Component for displaying citation distribution visualization."""
    
    def __init__(self, data=None, **kwargs):
        """
        Initialize the citation distribution component.
        
        Args:
            data: Main publications DataFrame
        """
        super().__init__(data=data, **kwargs)
    
    def render(self) -> None:
        """Render the citation distribution component."""
        if not self.validate_data():
            st.warning("No data available to display citation distribution.")
            return
        
        # Create citation distribution histogram
        fig_dist = px.histogram(
            self.data,
            x='times_cited',
            nbins=20,
            title="Distribution of Citations",
            labels={'times_cited': 'Number of Citations', 'count': 'Number of Publications'}
        )
        fig_dist.update_layout(height=400)
        st.plotly_chart(fig_dist, use_container_width=True)

