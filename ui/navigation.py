from __future__ import annotations

from html import escape

import streamlit as st


PAGES = ["Home", "Workspace", "Algorithm"]


def get_current_page() -> str:
    page = st.query_params.get("page", "Home")
    if page not in PAGES:
        return "Home"
    return page


def set_current_page(page: str) -> None:
    st.query_params["page"] = page
    st.session_state["current_page"] = page


def render_navigation(current: str) -> None:
    links = []
    for page in PAGES:
        class_name = "active" if page == current else ""
        links.append(f'<a class="{class_name}" href="?page={escape(page)}">{escape(page)}</a>')
    st.markdown(
        f"""
        <div class="top-nav">
            <a class="brand" href="?page=Home">Panorama Vision</a>
            <nav class="nav-links">{''.join(links)}</nav>
        </div>
        """,
        unsafe_allow_html=True,
    )
