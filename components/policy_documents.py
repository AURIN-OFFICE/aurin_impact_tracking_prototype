"""
Policy documents component for displaying policy documents relevant to AURIN.
"""
from components.base_component import BaseComponent
import streamlit as st
import pandas as pd


class PolicyDocumentsComponent(BaseComponent):
    """Component for displaying policy documents referencing AURIN."""

    def __init__(self, data: pd.DataFrame = None, **kwargs):
        super().__init__(data=data, **kwargs)

    def render(self) -> None:
        """Render the policy documents component."""
        st.markdown(
            '<div class="section-header">📄 Policy Documents Referencing AURIN</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Policy documents discovered via full-text search for "
            '"Australian Urban Research Infrastructure Network" or "AURIN" '
            "in the Dimensions Policy Documents database."
        )

        if not self.validate_data():
            st.info("No policy documents found for AURIN.")
            return

        df = self.data.copy()

        # ── column selection ────────────────────────────────────────────────
        col_map = {}
        if "title" in df.columns:
            col_map["title"] = "Title"
        if "year" in df.columns:
            col_map["year"] = "Year"
        if "publisher_org.name" in df.columns:
            col_map["publisher_org.name"] = "Publisher"
        if "publisher_org.country_name" in df.columns:
            col_map["publisher_org.country_name"] = "Country"
        if "linkout" in df.columns:
            col_map["linkout"] = "Link"

        available_cols = [c for c in col_map if c in df.columns]
        if not available_cols:
            st.dataframe(df, use_container_width=True, hide_index=True)
            return

        display_df = df[available_cols].rename(columns=col_map)

        # Sort by year descending
        if "Year" in display_df.columns:
            display_df = display_df.sort_values("Year", ascending=False, na_position="last")

        # Make Link column clickable
        if "Link" in display_df.columns:
            display_df["Link"] = display_df["Link"].apply(
                lambda url: f"[Open]({url})" if pd.notna(url) and url else ""
            )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Link": st.column_config.LinkColumn("Link", display_text="Open"),
            } if "Link" in display_df.columns else None,
        )

        st.caption(f"Total: {len(display_df)} policy document(s) found.")

        # Download
        csv_df = df[available_cols].rename(columns=col_map)
        csv = csv_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download policy documents as CSV",
            data=csv,
            file_name="aurin_policy_documents.csv",
            mime="text/csv",
        )
