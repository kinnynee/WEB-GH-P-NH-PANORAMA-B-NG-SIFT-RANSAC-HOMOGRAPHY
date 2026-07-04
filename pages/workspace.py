from __future__ import annotations

from pathlib import Path

import streamlit as st

from models.result_models import ImageInput, StitchSettings, UserFacingError
from services.export_service import panorama_download_bytes, results_zip_bytes
from services.processing_service import build_image_inputs, run_panorama_pipeline
from ui.components import metric_strip, render_error


SAMPLE_DIR = Path(__file__).resolve().parents[1] / "data" / "sample"


def _init_state() -> None:
    st.session_state.setdefault("project_files", [])
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("last_error", None)


def _settings_from_widgets() -> StitchSettings:
    return StitchSettings(
        matcher=st.session_state.get("matcher", "BFMatcher"),
        lowe_ratio=float(st.session_state.get("lowe_ratio", 0.75)),
        ransac_threshold=float(st.session_state.get("ransac_threshold", 5.0)),
        blend_mode=st.session_state.get("blend_mode", "Feather"),
    )


def render_workspace() -> None:
    _init_state()
    st.markdown(
        """
        <h1>Panorama Workspace</h1>
        <p class="lead">Configure parameters and process overlapping images into a seamless panorama.</p>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([0.36, 0.64], gap="large")
    with left:
        _render_upload_panel()
        _render_settings_panel()
    with right:
        _render_results_panel()


def _render_upload_panel() -> None:
    with st.container(border=True):
        st.subheader("Upload Images")
        uploaded = st.file_uploader(
            "Upload 2 to 4 overlapping images",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            label_visibility="visible",
        )
        if uploaded:
            existing = {(item["name"], len(item["data"])) for item in st.session_state.project_files}
            for file in uploaded:
                data = file.getvalue()
                key = (file.name, len(data))
                if key not in existing and len(st.session_state.project_files) < 4:
                    st.session_state.project_files.append({"name": file.name, "data": data})
                    existing.add(key)
            if len(uploaded) > 4 or len(st.session_state.project_files) > 4:
                st.warning("This version supports up to 4 images. Extra files were ignored.")

        if st.button("Load Sample Images", width="stretch"):
            st.session_state.project_files = [
                {"name": path.name, "data": path.read_bytes()}
                for path in [
                    SAMPLE_DIR / "sample_01_left.png",
                    SAMPLE_DIR / "sample_02_center.png",
                    SAMPLE_DIR / "sample_03_right.png",
                    SAMPLE_DIR / "sample_04_far_right.png",
                ]
            ]
            st.session_state.result = None
            st.session_state.last_error = None
            st.rerun()

        if not st.session_state.project_files:
            st.info("Add 2-4 JPG, JPEG, or PNG files.")
            return

        for index, item in enumerate(list(st.session_state.project_files)):
            with st.container(border=True):
                image_bytes = item["data"]
                st.image(image_bytes, width=120)
                st.markdown(f"**{index + 1}. {item['name']}**")
                size_kb = len(image_bytes) / 1024
                st.caption(f"{size_kb:.1f} KB")
                cols = st.columns(3)
                with cols[0]:
                    if st.button("Left", key=f"left_{index}", disabled=index == 0, width="stretch"):
                        _move_image(index, -1)
                with cols[1]:
                    if st.button("Right", key=f"right_{index}", disabled=index == len(st.session_state.project_files) - 1, width="stretch"):
                        _move_image(index, 1)
                with cols[2]:
                    if st.button("Delete", key=f"delete_{index}", width="stretch"):
                        del st.session_state.project_files[index]
                        st.session_state.result = None
                        st.rerun()


def _move_image(index: int, delta: int) -> None:
    files = st.session_state.project_files
    new_index = index + delta
    files[index], files[new_index] = files[new_index], files[index]
    st.session_state.result = None
    st.rerun()


def _render_settings_panel() -> None:
    with st.container(border=True):
        st.subheader("Settings")
        st.selectbox("Matcher", ["BFMatcher", "FLANN"], key="matcher")
        st.slider("Lowe Ratio", min_value=0.50, max_value=0.95, value=0.75, step=0.01, key="lowe_ratio")
        st.slider("RANSAC Threshold", min_value=1.0, max_value=10.0, value=5.0, step=0.5, key="ransac_threshold")
        st.selectbox("Blending", ["Feather", "Simple"], key="blend_mode")

        can_run = 2 <= len(st.session_state.project_files) <= 4
        if st.button("Create Panorama", type="primary", disabled=not can_run, width="stretch"):
            _process_project()
        if not can_run:
            st.caption("Create Panorama is enabled when 2-4 valid images are available.")


def _process_project() -> None:
    settings = _settings_from_widgets()
    progress = st.progress(0)
    status = st.empty()
    try:
        status.write("Detecting Features")
        progress.progress(15)
        files = [(item["name"], item["data"]) for item in st.session_state.project_files]
        images = build_image_inputs(files, settings)
        status.write("Matching Images")
        progress.progress(35)
        status.write("Filtering Matches")
        progress.progress(60)
        status.write("Creating Panorama")
        result = run_panorama_pipeline(images, settings)
        progress.progress(100)
        status.success("Panorama created successfully.")
        st.session_state.result = result
        st.session_state.last_error = None
    except UserFacingError as error:
        progress.progress(100)
        st.session_state.result = None
        st.session_state.last_error = error


def _render_results_panel() -> None:
    with st.container(border=True):
        result = st.session_state.result
        error = st.session_state.last_error
        _render_latest_result_preview(result, error)

        tabs = st.tabs(["Input", "Keypoints", "Matching", "RANSAC", "Homography", "Panorama"])
        selected_pair_index = _select_pair_index(result)

        with tabs[0]:
            _render_input_tab()
        with tabs[1]:
            _render_keypoints_tab(result, selected_pair_index)
        with tabs[2]:
            _render_matching_tab(result, selected_pair_index)
        with tabs[3]:
            _render_ransac_tab(result, selected_pair_index)
        with tabs[4]:
            _render_homography_tab(result, selected_pair_index)
        with tabs[5]:
            _render_panorama_tab(result, error)


def _render_latest_result_preview(result, error) -> None:
    if error:
        render_error(error)
        st.divider()
        return
    if not result:
        return

    st.markdown("### Latest Panorama")
    st.image(result.final_panorama, caption="Final panorama result", width="stretch")
    height, width = result.final_panorama.shape[:2]
    metric_strip(
        [
            ("Images Used", str(len(result.input_images))),
            ("Final Resolution", f"{width} x {height}"),
            ("Processing Time", f"{result.processing_time:.2f}s"),
        ]
    )
    st.divider()


def _render_input_tab() -> None:
    if not st.session_state.project_files:
        st.info("Uploaded images will appear here.")
        return
    settings = _settings_from_widgets()
    try:
        images = build_image_inputs([(item["name"], item["data"]) for item in st.session_state.project_files], settings)
    except UserFacingError as error:
        render_error(error)
        return
    cols = st.columns(min(4, len(images)))
    for index, image in enumerate(images):
        with cols[index % len(cols)]:
            st.image(image.image, width="stretch")
            st.markdown(f"**{index + 1}. {image.name}**")
            st.caption(f"{image.size[0]} x {image.size[1]} px")


def _select_pair_index(result) -> int:
    if not result or not result.pair_results:
        return 0
    labels = [f"Pair {pair.pair_index}: {pair.base_name} + {pair.next_name}" for pair in result.pair_results]
    if len(labels) == 1:
        return 0
    return st.selectbox(
        "Result Pair",
        range(len(labels)),
        format_func=lambda i: labels[i],
        key="result_pair_selector",
    )


def _render_keypoints_tab(result, selected_pair_index: int) -> None:
    if not result:
        st.info("Run the pipeline to view SIFT keypoints.")
        return
    pair = result.pair_results[selected_pair_index]
    cols = st.columns(2)
    for col, feature in zip(cols, [pair.base_features, pair.next_features]):
        with col:
            st.image(feature.visualization, width="stretch")
            st.metric(f"{feature.image_name} Keypoints", f"{feature.keypoint_count:,}")


def _render_matching_tab(result, selected_pair_index: int) -> None:
    if not result:
        st.info("Run the pipeline to view raw and Lowe-filtered matches.")
        return
    pair = result.pair_results[selected_pair_index]
    metric_strip(
        [
            ("Raw Matches", f"{pair.matches.raw_count:,}"),
            ("Good Matches", f"{pair.matches.good_count:,}"),
            ("Retention Rate", f"{pair.matches.retention_rate:.1%}"),
        ]
    )
    st.image(pair.matches.good_visualization, caption="Good matches after Lowe Ratio Test", width="stretch")
    with st.expander("Raw match visualization"):
        st.image(pair.matches.raw_visualization, width="stretch")


def _render_ransac_tab(result, selected_pair_index: int) -> None:
    if not result:
        st.info("Run the pipeline to view RANSAC inliers.")
        return
    pair = result.pair_results[selected_pair_index]
    metric_strip(
        [
            ("Good Matches", f"{pair.matches.good_count:,}"),
            ("RANSAC Inliers", f"{pair.homography.inlier_count:,}"),
            ("Outliers Removed", f"{pair.homography.outlier_count:,}"),
        ]
    )
    st.metric("Inlier Ratio", f"{pair.homography.inlier_ratio:.1%}")
    st.image(pair.ransac_visualization, caption="RANSAC inlier matches", width="stretch")


def _render_homography_tab(result, selected_pair_index: int) -> None:
    if not result:
        st.info("Run the pipeline to view the Homography matrix.")
        return
    pair = result.pair_results[selected_pair_index]
    h = pair.homography.matrix
    matrix_text = "\n".join(" ".join(f"{value: .6f}" for value in row) for row in h)
    st.code(matrix_text, language="text")
    metric_strip(
        [
            ("RANSAC Threshold", f"{result.settings.ransac_threshold:.1f} px"),
            ("Inliers", f"{pair.homography.inlier_count:,}"),
            ("Status", pair.homography.status),
        ]
    )
    st.image(pair.warped_visualization, caption="Warped shared canvas preview", width="stretch")


def _render_panorama_tab(result, error) -> None:
    if error:
        render_error(error)
    if not result:
        st.info("The final panorama will appear here after processing.")
        return
    st.image(result.final_panorama, width="stretch")
    height, width = result.final_panorama.shape[:2]
    metric_strip(
        [
            ("Images Used", str(len(result.input_images))),
            ("Final Resolution", f"{width} x {height}"),
            ("Processing Time", f"{result.processing_time:.2f}s"),
        ]
    )
    cols = st.columns(3)
    with cols[0]:
        st.download_button(
            "Download Panorama",
            data=panorama_download_bytes(result),
            file_name="panorama_result.jpg",
            mime="image/jpeg",
            width="stretch",
        )
    with cols[1]:
        st.download_button(
            "Download All Results",
            data=results_zip_bytes(result),
            file_name="panorama_results.zip",
            mime="application/zip",
            width="stretch",
        )
    with cols[2]:
        if st.button("Start New Project", width="stretch"):
            st.session_state.project_files = []
            st.session_state.result = None
            st.session_state.last_error = None
            st.rerun()
