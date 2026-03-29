"""
SDG categories component for displaying Sustainable Development Goals breakdown.
"""
from components.base_component import BaseComponent
from typing import Optional
import streamlit as st
import pandas as pd
import plotly.express as px


class SDGCategoriesComponent(BaseComponent):
    """Component for displaying paper counts by Sustainable Development Goal (SDG) category."""

    def __init__(self, data: Optional[pd.DataFrame] = None, **kwargs):
        super().__init__(data=data, **kwargs)

    def _parse_categories(self) -> Optional[pd.DataFrame]:
        """Explode category_sdg into one row per category and return counts."""
        if 'category_sdg' not in self.data.columns:
            return None

        df = self.data[['id', 'category_sdg']].dropna(subset=['category_sdg'])
        if df.empty:
            return None

        rows = []
        for _, row in df.iterrows():
            cats = row['category_sdg']
            if not isinstance(cats, list):
                continue
            for cat in cats:
                if isinstance(cat, dict):
                    name = cat.get('name') or cat.get('id', '')
                elif isinstance(cat, str):
                    name = cat
                else:
                    continue
                if name:
                    rows.append(name)

        if not rows:
            return None

        counts = pd.Series(rows).value_counts().reset_index()
        counts.columns = ['SDG', 'Papers']
        return counts

    def render(self) -> None:
        """Render the SDG categories component."""
        if not self.validate_data():
            st.info("No SDG category data available.")
            return

        counts = self._parse_categories()
        if counts is None or counts.empty:
            st.info("No SDG categories found in the data.")
            return

        st.markdown('<div class="section-header">🌱 Sustainable Development Goals (SDG)</div>', unsafe_allow_html=True)

        top5 = counts.head(5)

        # Top 5 highlight cards
        st.markdown("**Top 5 SDGs**")
        cols = st.columns(5)
        for i, (_, row) in enumerate(top5.iterrows()):
            with cols[i]:
                st.metric(label=row['SDG'], value=f"{row['Papers']} papers")

        with st.expander(f"View all {len(counts)} SDGs"):
            fig = px.bar(
                counts,
                x='Papers',
                y='SDG',
                orientation='h',
                title="Papers by Sustainable Development Goal",
                labels={'Papers': 'Number of Papers', 'SDG': ''},
                color='Papers',
                color_continuous_scale='Greens',
            )
            fig.update_layout(
                height=max(400, len(counts) * 28),
                yaxis={'categoryorder': 'total ascending'},
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)
