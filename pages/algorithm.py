from __future__ import annotations

import streamlit as st

from utils.visualization import make_placeholder_illustration


SECTIONS = [
    ("SIFT", "Detects stable keypoints and computes 128-dimensional descriptors that survive moderate scale and rotation changes.", "Find repeatable visual anchors in each input image.", "sift"),
    ("Feature Matching", "Compares SIFT descriptors between adjacent images with KNN matching.", "Build candidate correspondences between left and right frames.", "matching"),
    ("Lowe Ratio Test", "Keeps a match only when the nearest descriptor is clearly better than the second nearest descriptor.", "Remove ambiguous matches before geometry estimation.", "matching"),
    ("RANSAC", "Repeatedly estimates a transform from small random samples and keeps matches that agree with the dominant geometry.", "Separate inliers from outliers.", "ransac"),
    ("Homography", "Computes a 3x3 projective matrix that maps one image plane into another.", "Align adjacent images on a shared panorama canvas.", "homography"),
    ("Warping", "Transforms image pixels with the estimated Homography and expands the canvas from transformed corners.", "Place images in one coordinate system without hardcoded canvas sizes.", "homography"),
    ("Blending", "Combines overlapping valid pixels with simple averaging or distance-based feather weights.", "Reduce visible seams in overlap regions.", "matching"),
]


def render_algorithm() -> None:
    st.markdown(
        """
        <div style="max-width:760px;margin-bottom:34px;">
            <h1 style="color:#0058be;">Algorithm Architecture</h1>
            <p class="lead">The core sequence of the Panorama Vision pipeline. A compact overview of the computational steps required for seamless image stitching.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for index, (title, description, role, visual) in enumerate(SECTIONS, start=1):
        st.markdown('<div class="algorithm-row">', unsafe_allow_html=True)
        left, right = st.columns([1.2, 1])
        with left:
            st.markdown(f'<div class="algorithm-step">Step {index:02d}</div>', unsafe_allow_html=True)
            st.subheader(title)
            st.write(description)
            st.caption(f"Role: {role}")
        with right:
            st.image(make_placeholder_illustration(visual), width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)
