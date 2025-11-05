"""
Header component for the dashboard.
"""
from components.base_component import BaseComponent
import streamlit as st
import datetime


class HeaderComponent(BaseComponent):
    """Component for rendering the dashboard header."""
    
    def __init__(self, **kwargs):
        """Initialize the header component."""
        super().__init__(**kwargs)
        self._inject_custom_css()
    
    def _inject_custom_css(self) -> None:
        """Inject custom CSS styles for the dashboard."""
        st.markdown("""
        <style>
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                color: #1f77b4;
                text-align: center;
                margin-bottom: 2rem;
            }
            .metric-card {
                background-color: #f0f2f6;
                padding: 1rem;
                border-radius: 0.5rem;
                border-left: 4px solid #1f77b4;
            }
            .section-header {
                font-size: 1.5rem;
                font-weight: bold;
                color: #2c3e50;
                margin-top: 2rem;
                margin-bottom: 1rem;
            }
        </style>
        """, unsafe_allow_html=True)
    
    def render(self) -> None:
        """Render the header component."""
        st.markdown('<h1 class="main-header">📊 AURIN Impact Tracking Dashboard</h1>', unsafe_allow_html=True)
        st.markdown(f"**Last Updated:** {datetime.date.today().strftime('%B %d, %Y')}")

