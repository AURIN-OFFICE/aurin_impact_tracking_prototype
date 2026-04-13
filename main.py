"""
Main Streamlit application for AURIN Impact Tracking Dashboard.
This file orchestrates all components and data loading.
"""
import streamlit as st

from data_loader import DimensionsDataLoader, PolicyDocumentsDataLoader, GrantsDataLoader, PatentsDataLoader, ResearchTrendMonitorDataLoader, GrantTrendMonitorDataLoader
from components.sidebar import SidebarComponent
from components.header import HeaderComponent
from components.research_papers import (
    KeyMetricsComponent,
    TrendsComponent,
    TopCitedArticlesComponent,
    RecentPapersComponent,
    ResearchCategoriesComponent,
    SDGCategoriesComponent,
    ConceptsComponent,
)
from components.research_organisations import AffiliatedOrganisationsComponent, AffiliatedCountriesComponent
from components.policy_documents import PolicyDocumentsComponent
from components.patents import PatentsComponent
from components.aurin_fundings import GrantsComponent
from components.research_trend import ResearchTrendMonitorComponent
from components.grant_trend import GrantTrendMonitorComponent
from components.ai_summary import AISummaryComponent
from components.ai_summary.gemini_provider import GeminiProvider


# Page configuration
st.set_page_config(
    page_title="AURIN Impact Tracking Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
sidebar = SidebarComponent()
header = HeaderComponent()

# Sidebar: navigation + config
sidebar.render()

# Header: title
header.render()

# Retrieve credentials and active tab
api_key = sidebar.get_api_key()
gemini_api_key = sidebar.get_gemini_api_key()
from_date, to_date = sidebar.get_date_range()
active_tab = sidebar.get_active_tab()

# Convert date objects to strings in YYYY-MM-DD format if they exist
from_date_str = from_date.strftime("%Y-%m-%d") if from_date else None
to_date_str = to_date.strftime("%Y-%m-%d") if to_date else None

# Load data
data_loader = DimensionsDataLoader()

_LOAD_STEPS = [
    "Fetching AURIN publications...",
    "Fetching policy documents...",
    "Fetching patents...",
    "Fetching grants...",
    "Fetching 10-year research trends...",
    "Fetching 10-year grant trends...",
]
_STEP_PROGRESS = [10, 20, 30, 40, 80, 100]

if api_key:
    _progress = st.progress(0, text=_LOAD_STEPS[0])
    with st.status("Loading dashboard data…", expanded=False) as _load_status:
        df_aurin_main, df_authors, df_affiliations, df_funders, df_investigators = data_loader.load_data(
            api_key, from_date=from_date_str, to_date=to_date_str
        )
        _progress.progress(_STEP_PROGRESS[0], text=_LOAD_STEPS[1])

        if df_aurin_main is not None:
            df_policies = PolicyDocumentsDataLoader().load_data(api_key, from_date=from_date_str, to_date=to_date_str)
            _progress.progress(_STEP_PROGRESS[1], text=_LOAD_STEPS[2])

            df_patents = PatentsDataLoader().load_data(api_key, from_date=from_date_str, to_date=to_date_str)
            _progress.progress(_STEP_PROGRESS[2], text=_LOAD_STEPS[3])

            df_grants = GrantsDataLoader().load_data(api_key, from_date=from_date_str, to_date=to_date_str)
            _progress.progress(_STEP_PROGRESS[3], text=_LOAD_STEPS[4])

            df_trend_monitor = ResearchTrendMonitorDataLoader().load_data(api_key)
            _progress.progress(_STEP_PROGRESS[4], text=_LOAD_STEPS[5])

            df_grant_trend_monitor = GrantTrendMonitorDataLoader().load_data(api_key)
            _progress.progress(100, text="All data loaded.")
            _progress.empty()

            _load_status.update(label="Dashboard data loaded.", state="complete")
        else:
            df_policies = df_patents = df_grants = df_trend_monitor = df_grant_trend_monitor = None
            _progress.empty()
            _load_status.update(label="Failed to load data.", state="error")
else:
    df_aurin_main, df_authors, df_affiliations, df_funders, df_investigators = None, None, None, None, None
    df_policies = df_patents = df_grants = df_trend_monitor = df_grant_trend_monitor = None

# Render the active section
if df_aurin_main is not None:
    if active_tab == "ai_summary":
        AISummaryComponent(
            main_data=df_aurin_main,
            affiliations_data=df_affiliations,
            policies_data=df_policies,
            patents_data=df_patents,
            grants_data=df_grants,
            date_from=from_date_str,
            date_to=to_date_str,
            provider=GeminiProvider(api_key=gemini_api_key),
        ).render()

    elif active_tab == "research_papers":
        KeyMetricsComponent(main_data=df_aurin_main, affiliations_data=df_affiliations).render()
        TrendsComponent(data=df_aurin_main).render()
        TopCitedArticlesComponent(data=df_aurin_main).render()
        RecentPapersComponent(data=df_aurin_main).render()
        ResearchCategoriesComponent(data=df_aurin_main).render()
        SDGCategoriesComponent(data=df_aurin_main).render()
        ConceptsComponent(data=df_aurin_main).render()

    elif active_tab == "research_organisations":
        AffiliatedOrganisationsComponent(main_data=df_aurin_main, affiliations_data=df_affiliations).render()
        AffiliatedCountriesComponent(affiliations_data=df_affiliations).render()

    elif active_tab == "policy_documents":
        PolicyDocumentsComponent(data=df_policies).render()

    elif active_tab == "patents":
        PatentsComponent(data=df_patents).render()

    elif active_tab == "aurin_fundings":
        GrantsComponent(data=df_grants).render()

    elif active_tab == "research_trend_monitor":
        ResearchTrendMonitorComponent(publications_data=df_trend_monitor).render()

    elif active_tab == "grant_trend_monitor":
        GrantTrendMonitorComponent(grants_data=df_grant_trend_monitor).render()

else:
    if not api_key:
        st.info("👈 Please configure your Dimensions API key using the sidebar to load the dashboard.")
    else:
        st.error("Failed to load data. Please check your API credentials and connection.")
