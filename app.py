from __future__ import annotations

import streamlit as st

from pages.algorithm import render_algorithm
from pages.home import render_home
from pages.workspace import render_workspace
from ui.navigation import get_current_page, render_navigation
from ui.styles import apply_global_styles


st.set_page_config(
    page_title="Panorama Vision Studio",
    page_icon="PV",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_global_styles()
current_page = get_current_page()
render_navigation(current_page)

if current_page == "Workspace":
    render_workspace()
elif current_page == "Algorithm":
    render_algorithm()
else:
    render_home()

st.markdown(
    """
    <div style="border-top:1px solid #c2c6d6;margin-top:48px;padding-top:24px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;color:#424754;">
        <strong>Panorama Vision</strong>
        <span>© 2026 Panorama Vision Studio. Academic Research Project.</span>
    </div>
    """,
    unsafe_allow_html=True,
)
