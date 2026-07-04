from __future__ import annotations

from pathlib import Path

import streamlit as st

from ui.navigation import set_current_page


SAMPLE_DIR = Path(__file__).resolve().parents[1] / "data" / "sample"


def render_home() -> None:
    st.markdown(
        """
        <section class="hero">
            <div>
                <h1>Create Panorama Images Easily</h1>
                <p>Upload multiple overlapping images and combine them into one Panorama using SIFT, RANSAC and Homography.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )
    col_text, col_visual = st.columns([0.95, 1.05])
    with col_text:
        c1, c2 = st.columns([1, 1.1])
        with c1:
            if st.button("Start Stitching", type="primary", width="stretch"):
                set_current_page("Workspace")
                st.rerun()
        with c2:
            if st.button("Learn Algorithm", width="stretch"):
                set_current_page("Algorithm")
                st.rerun()
    with col_visual:
        with st.container(border=True):
            imgs = [
                SAMPLE_DIR / "sample_01_left.png",
                SAMPLE_DIR / "sample_02_center.png",
                SAMPLE_DIR / "sample_03_right.png",
            ]
            image_cols = st.columns(3)
            for col, path in zip(image_cols, imgs):
                with col:
                    st.image(str(path), width="stretch")
            st.markdown("<div style='text-align:center;color:#727785;font-size:26px;'>down</div>", unsafe_allow_html=True)
            st.image(str(SAMPLE_DIR / "sample_full_reference.png"), width="stretch")
    st.markdown("</section>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="pipeline-row">
            <div><div class="step-number">1</div><h3>Upload Images</h3><p class="lead">Provide a sequence of overlapping photographs.</p></div>
            <div><div class="step-number">2</div><h3>Detect Features</h3><p class="lead">SIFT identifies stable local keypoints and descriptors.</p></div>
            <div><div class="step-number">3</div><h3>Match Images</h3><p class="lead">Lowe Ratio and RANSAC filter unreliable matches.</p></div>
            <div><div class="step-number">4</div><h3>Create Panorama</h3><p class="lead">Homography warps and blends the final output.</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
