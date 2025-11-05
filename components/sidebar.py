"""
Sidebar component for API key management and configuration.
"""
from components.base_component import BaseComponent
import streamlit as st
from pathlib import Path


class SidebarComponent(BaseComponent):
    """Component for managing sidebar configuration and API key."""
    
    def __init__(self, **kwargs):
        """Initialize the sidebar component."""
        super().__init__(**kwargs)
        self._initialize_session_state()
    
    def _initialize_session_state(self) -> None:
        """Initialize session state variables if they don't exist."""
        if 'api_key' not in st.session_state:
            st.session_state.api_key = None
        if 'api_key_input' not in st.session_state:
            st.session_state.api_key_input = ""
    
    def _render_logo(self) -> None:
        """Render AURIN logo at the top of the sidebar."""
        logo_path = "https://data.aurin.org.au/assets/aurin-logo-400-D0zkc36m.png"
        st.sidebar.image(logo_path, use_container_width=True)
    
    def render(self) -> None:
        """Render the sidebar component."""
        # Add AURIN logo at the top
        self._render_logo()
        
        st.sidebar.header("🔧 Configuration")
        st.sidebar.info("This dashboard displays AURIN research impact metrics and analytics.")
        
        # API Key input
        api_key_input = st.sidebar.text_input(
            "Dimensions API Key",
            type="password",
            help="Enter your Dimensions API key to access the data",
            placeholder="Enter your API key here...",
            value=st.session_state.get('api_key_input', '')
        )
        
        # Button row for API key actions
        with st.sidebar:
            submit_key = st.button("🔑 Submit Key", type="primary", use_container_width=True)
            clear_key = st.button("🗑️ Clear", use_container_width=True)
        
        # Handle API key submission
        if submit_key and api_key_input:
            st.session_state.api_key = api_key_input
            st.session_state.api_key_input = api_key_input
            st.sidebar.success("✅ API key submitted successfully!")
            st.rerun()
        elif submit_key and not api_key_input:
            st.sidebar.error("❌ Please enter an API key before submitting")
        
        # Handle API key clearing
        if clear_key:
            st.session_state.api_key = None
            st.session_state.api_key_input = ""
            st.sidebar.info("🗑️ API key cleared")
            st.rerun()
        
        # Store the input value in session state for persistence
        if api_key_input != st.session_state.get('api_key_input', ''):
            st.session_state.api_key_input = api_key_input
        
        # Show status
        if st.session_state.get('api_key'):
            st.sidebar.success("✅ API key is active")
        else:
            st.sidebar.warning("⚠️ Please enter and submit your API key to load data")
    
    def get_api_key(self) -> str:
        """
        Get the current API key from session state.
        
        Returns:
            API key string or None
        """
        return st.session_state.get('api_key')

