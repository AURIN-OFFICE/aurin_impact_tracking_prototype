"""
Affiliated countries component for displaying geographic impact.
"""
from components.base_component import BaseComponent
from typing import Optional
import streamlit as st
import pandas as pd
import plotly.express as px


class AffiliatedCountriesComponent(BaseComponent):
    """Component for displaying affiliated countries analysis."""
    
    def __init__(self, affiliations_data: Optional[pd.DataFrame] = None, **kwargs):
        """
        Initialize the affiliated countries component.
        
        Args:
            affiliations_data: Affiliations DataFrame
        """
        super().__init__(data=affiliations_data, **kwargs)
    
    def render(self) -> None:
        """Render the affiliated countries component."""
        if not self.validate_data():
            st.info("No affiliated countries found.")
            return
        
        st.markdown('<div class="section-header">🌍 Affiliated Countries We Had Impact On</div>', unsafe_allow_html=True)
        
        # Get unique countries (drop empty records)
        affiliated_countries = self.data[self.data['aff_country'].notna() & (self.data['aff_country'] != '')]['aff_country'].unique()
        
        if len(affiliated_countries) > 0:
            # Create a DataFrame for better display
            country_df = pd.DataFrame({
                'Country': affiliated_countries
            }).sort_values('Country')
            
            # Display in columns
            cols = st.columns(4)
            for i, country in enumerate(country_df['Country']):
                with cols[i % 4]:
                    st.write(f"• {country}")
            
            # Create a world map visualization
            country_counts = self.data[self.data['aff_country'].notna() & (self.data['aff_country'] != '')]['aff_country'].value_counts()
            
            fig_countries = px.pie(
                values=country_counts.values,
                names=country_counts.index,
                title="Distribution of Publications by Country"
            )
            fig_countries.update_layout(height=500)
            st.plotly_chart(fig_countries, use_container_width=True)
        else:
            st.info("No affiliated countries found.")

