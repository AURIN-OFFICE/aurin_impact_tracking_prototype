import streamlit as st
import requests
import dimcli
from dimcli.utils import *
import json
import sys
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="AURIN Impact Tracking Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'api_key_input' not in st.session_state:
    st.session_state.api_key_input = ""

# Custom CSS for better styling
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

# Header
st.markdown('<h1 class="main-header">📊 AURIN Impact Tracking Dashboard</h1>', unsafe_allow_html=True)
st.markdown(f"**Last Updated:** {datetime.date.today().strftime('%B %d, %Y')}")

# Sidebar for configuration
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
# col1, col2 = st.sidebar.columns(2)

# with col1:
    

# with col2:
    

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

# Data loading section
@st.cache_data
def load_aurin_data(api_key):
    """Load and process AURIN data from Dimensions API"""
    try:
        if not api_key:
            st.error("Please enter your Dimensions API key in the sidebar to load data.")
            return None, None, None, None, None
            
        ENDPOINT = "https://app.dimensions.ai"
        
        dimcli.login(key=api_key, endpoint=ENDPOINT)
        dsl = dimcli.Dsl()
        
        query = """
            search publications for "\\"Australian Urban Research Infrastructure Network\\""
            return publications[id+title+authors+pages+type+volume+issue+journal+times_cited+date+date_online]
        """
        
        res_aurin = dsl.query_iterative(query)
        df_aurin_main = res_aurin.as_dataframe()
        df_authors = res_aurin.as_dataframe_authors()
        df_affiliations = res_aurin.as_dataframe_authors_affiliations()
        df_funders = res_aurin.as_dataframe_funders()
        df_investigators = res_aurin.as_dataframe_investigators()
        
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

# Load data
if st.session_state.api_key:
    with st.spinner("Loading AURIN data from Dimensions API..."):
        df_aurin_main, df_authors, df_affiliations, df_funders, df_investigators = load_aurin_data(st.session_state.api_key)
else:
    df_aurin_main, df_authors, df_affiliations, df_funders, df_investigators = None, None, None, None, None

if df_aurin_main is not None:
    # Calculate metrics
    top_5_cited_articles = df_aurin_main.nlargest(5, 'times_cited')
    affiliated_organisations_we_had_impact_on = df_affiliations['aff_name'].unique()
    affiliated_countries_we_had_impact_on = df_affiliations['aff_country'].unique()
    top_5_most_recent_aurin_papers = df_aurin_main.sort_values(by='date', ascending=False).head(5)
    aurin_total_citation = df_aurin_main['times_cited'].sum()
    
    # Filter papers from last 6 months
    six_months_ago = datetime.datetime.now() - datetime.timedelta(days=180)
    df_aurin_main['date'] = pd.to_datetime(df_aurin_main['date'], errors='coerce')
    recent_6_months_papers = df_aurin_main[df_aurin_main['date'] >= six_months_ago].sort_values(by='date', ascending=False)
    
    # Key Metrics Row
    st.markdown('<div class="section-header">📈 Key Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Publications",
            value=len(df_aurin_main),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Citations",
            value=f"{aurin_total_citation:,}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Affiliated Organisations",
            value=len(affiliated_organisations_we_had_impact_on),
            delta=None
        )
    
    with col4:
        st.metric(
            label="Affiliated Countries",
            value=len(affiliated_countries_we_had_impact_on),
            delta=None
        )
    
    # Top 5 Most Cited Articles
    st.markdown('<div class="section-header">🏆 Top 5 Most Cited Articles</div>', unsafe_allow_html=True)
    
    if not top_5_cited_articles.empty:
        # Create a more detailed table
        display_df = top_5_cited_articles[['title', 'times_cited', 'journal.title', 'date']].copy()
        display_df.columns = ['Title', 'Citations', 'Journal', 'Publication Date']
        display_df['Publication Date'] = pd.to_datetime(display_df['Publication Date']).dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Create a bar chart for citations
        fig_citations = px.bar(
            top_5_cited_articles,
            x='times_cited',
            y='title',
            orientation='h',
            title="Citation Count by Article",
            labels={'times_cited': 'Number of Citations', 'title': 'Article Title'},
            color='times_cited',
            color_continuous_scale='Blues'
        )
        fig_citations.update_layout(
            height=400,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        st.plotly_chart(fig_citations, use_container_width=True)
    else:
        st.info("No cited articles found.")
    
    # Affiliated Organisations
    st.markdown('<div class="section-header">🏢 Affiliated Organisations We Had Impact On</div>', unsafe_allow_html=True)
    
    if len(affiliated_organisations_we_had_impact_on) > 0:
        # Create comprehensive organization analysis
        if not df_affiliations.empty:
            # Calculate metrics per organization
            # Count publications per organization by counting rows
            org_metrics = df_affiliations.groupby('aff_name').agg({
                'aff_country': 'first'  # Get country for each org
            }).reset_index()
            
            # Add publication count by counting occurrences of each organization
            org_counts = df_affiliations['aff_name'].value_counts().reset_index()
            org_counts.columns = ['aff_name', 'publication_count']
            org_metrics = org_metrics.merge(org_counts, on='aff_name', how='left')
            
            # Add citation data if available
            if 'times_cited' in df_affiliations.columns:
                org_citations = df_affiliations.groupby('aff_name')['times_cited'].sum().reset_index()
                org_metrics = org_metrics.merge(org_citations, on='aff_name', how='left')
                org_metrics['times_cited'] = org_metrics['times_cited'].fillna(0)
            else:
                org_metrics['times_cited'] = 0
            
            # Sort by publication count (descending)
            org_metrics = org_metrics.sort_values('publication_count', ascending=False)
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Organizations", len(org_metrics))
            with col2:
                st.metric("Avg Publications/Org", f"{org_metrics['publication_count'].mean():.1f}")
            with col3:
                st.metric("Top Contributing Org", org_metrics.iloc[0]['aff_name'][:20] + "..." if len(org_metrics.iloc[0]['aff_name']) > 20 else org_metrics.iloc[0]['aff_name'])
            
            # Search and filter options
            st.subheader("🔍 Organization Explorer")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                search_term = st.text_input("Search organizations:", placeholder="Type to filter organizations...")
            with col2:
                sort_by = st.selectbox("Sort by:", ["Publications", "Citations", "Name", "Country"])
            
            # Filter organizations based on search
            if search_term:
                filtered_orgs = org_metrics[org_metrics['aff_name'].str.contains(search_term, case=False, na=False)]
            else:
                filtered_orgs = org_metrics.copy()
            
            # Sort based on selection
            if sort_by == "Publications":
                filtered_orgs = filtered_orgs.sort_values('publication_count', ascending=False)
            elif sort_by == "Citations":
                filtered_orgs = filtered_orgs.sort_values('times_cited', ascending=False)
            elif sort_by == "Name":
                filtered_orgs = filtered_orgs.sort_values('aff_name')
            elif sort_by == "Country":
                filtered_orgs = filtered_orgs.sort_values('aff_country')
            
            # Display filtered results
            if not filtered_orgs.empty:
                st.info(f"Showing {len(filtered_orgs)} organizations (filtered from {len(org_metrics)} total)")
                
                # Create expandable sections for top organizations
                st.subheader("🏆 Top Contributing Organizations")
                
                # Show top 10 in expandable format
                for i, (_, org) in enumerate(filtered_orgs.head(10).iterrows()):
                    with st.expander(f"#{i+1} {org['aff_name']} ({org['publication_count']} publications)"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Publications", org['publication_count'])
                        with col2:
                            st.metric("Total Citations", f"{org['times_cited']:,}")
                        with col3:
                            st.metric("Country", org['aff_country'])
                        
                        # Show publications from this organization
                        org_pubs = df_affiliations[df_affiliations['aff_name'] == org['aff_name']]
                        if not org_pubs.empty:
                            st.write("**Publications from this organization:**")
                            st.write(f"• {org['publication_count']} publications found")
                            # If we have publication IDs, we could link to main publications
                            if 'publication_id' in df_affiliations.columns:
                                pub_ids = org_pubs['publication_id'].unique()[:3]
                                for pub_id in pub_ids:
                                    st.write(f"• Publication ID: {pub_id}")
                            else:
                                st.write("• Publication details available in main dataset")
                
                # Interactive data table
                st.subheader("📊 Complete Organization Data")
                display_orgs = filtered_orgs[['aff_name', 'aff_country', 'publication_count', 'times_cited']].copy()
                display_orgs.columns = ['Organization', 'Country', 'Publications', 'Total Citations']
                display_orgs['Avg Citations'] = (display_orgs['Total Citations'] / display_orgs['Publications']).round(1)
                
                st.dataframe(
                    display_orgs,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    # Top 15 organizations by publications
                    top_15 = filtered_orgs.head(15)
                    fig_orgs = px.bar(
                        top_15,
                        x='publication_count',
                        y='aff_name',
                        orientation='h',
                        title="Top 15 Organizations by Publication Count",
                        labels={'publication_count': 'Number of Publications', 'aff_name': 'Organization'},
                        color='publication_count',
                        color_continuous_scale='Blues'
                    )
                    fig_orgs.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig_orgs, use_container_width=True)
                
                with col2:
                    # Organizations by country
                    country_org_counts = filtered_orgs.groupby('aff_country').size().sort_values(ascending=False)
                    fig_countries = px.pie(
                        values=country_org_counts.values,
                        names=country_org_counts.index,
                        title="Organizations by Country"
                    )
                    fig_countries.update_layout(height=500)
                    st.plotly_chart(fig_countries, use_container_width=True)
                
            else:
                st.warning("No organizations found matching your search criteria.")
        else:
            # Fallback to simple list if no detailed data
            org_df = pd.DataFrame({
                'Organisation': affiliated_organisations_we_had_impact_on
            }).sort_values('Organisation')
            
            st.dataframe(org_df, use_container_width=True, hide_index=True)
    else:
        st.info("No affiliated organisations found.")
    
    # Affiliated Countries
    st.markdown('<div class="section-header">🌍 Affiliated Countries We Had Impact On</div>', unsafe_allow_html=True)
    
    if len(affiliated_countries_we_had_impact_on) > 0:
        # Create a DataFrame for better display
        country_df = pd.DataFrame({
            'Country': affiliated_countries_we_had_impact_on
        }).sort_values('Country')
        
        # Display in columns
        cols = st.columns(4)
        for i, country in enumerate(country_df['Country']):
            with cols[i % 4]:
                st.write(f"• {country}")
        
        # Create a world map visualization (if we have country data)
        if not df_affiliations.empty:
            country_counts = df_affiliations['aff_country'].value_counts()
            
            fig_countries = px.pie(
                values=country_counts.values,
                names=country_counts.index,
                title="Distribution of Publications by Country"
            )
            fig_countries.update_layout(height=500)
            st.plotly_chart(fig_countries, use_container_width=True)
    else:
        st.info("No affiliated countries found.")
    
    # Top 5 Most Recent AURIN Papers
    st.markdown('<div class="section-header">📚 Top 5 Most Recent AURIN Papers</div>', unsafe_allow_html=True)
    
    if not top_5_most_recent_aurin_papers.empty:
        # Create a more detailed table
        recent_display_df = top_5_most_recent_aurin_papers[['title', 'date', 'journal.title', 'times_cited']].copy()
        recent_display_df.columns = ['Title', 'Publication Date', 'Journal', 'Citations']
        recent_display_df['Publication Date'] = pd.to_datetime(recent_display_df['Publication Date']).dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            recent_display_df,
            use_container_width=True,
            hide_index=True
        )
    
    # Papers Published in Last 6 Months
    st.markdown('<div class="section-header">📅 Papers Published in Last 6 Months</div>', unsafe_allow_html=True)
    
    if not recent_6_months_papers.empty:
        st.info(f"Found {len(recent_6_months_papers)} papers published in the last 6 months (since {six_months_ago.strftime('%B %d, %Y')})")
        
        # Create a more detailed table for recent papers
        recent_6m_display_df = recent_6_months_papers[['title', 'date', 'journal.title', 'times_cited']].copy()
        recent_6m_display_df.columns = ['Title', 'Publication Date', 'Journal', 'Citations']
        recent_6m_display_df['Publication Date'] = pd.to_datetime(recent_6m_display_df['Publication Date']).dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            recent_6m_display_df,
            use_container_width=True,
            hide_index=True
        )
        
        
    # Citation distribution
    fig_dist = px.histogram(
        df_aurin_main,
        x='times_cited',
        nbins=20,
        title="Distribution of Citations",
        labels={'times_cited': 'Number of Citations', 'count': 'Number of Publications'}
    )
    fig_dist.update_layout(height=400)
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("**Data Source:** Dimensions API | **Generated:** " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

else:
    if not st.session_state.api_key:
        st.info("👆 Please enter your Dimensions API key in the sidebar to load the dashboard data.")
    else:
        st.error("Failed to load data. Please check your API credentials and connection.")

