from __future__ import annotations

import streamlit as st

from models.result_models import UserFacingError


def metric_strip(items: list[tuple[str, str]]) -> None:
    html = ['<div class="meta-grid">']
    for label, value in items:
        html.append(
            f'<div><div class="meta-label">{label}</div><div class="mono" style="font-weight:700;">{value}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def render_error(error: UserFacingError) -> None:
    suggestions = "".join(f"<li>{item}</li>" for item in error.suggestions)
    st.markdown(
        f"""
        <div class="error-box">
            <strong style="color:#93000a;">{error.title}</strong>
            <p style="margin:8px 0;color:#424754;">{error.explanation}</p>
            <ul style="margin-bottom:0;color:#424754;">{suggestions}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
