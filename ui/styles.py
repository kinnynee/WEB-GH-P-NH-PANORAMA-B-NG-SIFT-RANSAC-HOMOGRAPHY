from __future__ import annotations

import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700&display=swap');

        :root {
            --background: #f9f9ff;
            --surface: #ffffff;
            --surface-low: #f2f3fd;
            --surface-variant: #e1e2ec;
            --primary: #0058be;
            --primary-hover: #2170e4;
            --text: #191b23;
            --muted: #424754;
            --outline: #c2c6d6;
            --danger: #ba1a1a;
        }

        .stApp {
            background: var(--background);
            color: var(--text);
            font-family: Inter, sans-serif;
        }

        [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
            display: none;
        }

        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        #MainMenu,
        footer {
            display: none !important;
        }

        .block-container {
            max-width: 1440px;
            padding-top: 1.25rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            font-family: Manrope, sans-serif !important;
            letter-spacing: 0;
        }

        .top-nav {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--outline);
            padding: 0 0 18px 0;
            margin-bottom: 30px;
        }

        .brand {
            color: var(--primary);
            font-family: Manrope, sans-serif;
            font-size: 26px;
            font-weight: 700;
            text-decoration: none !important;
        }

        .nav-links {
            display: flex;
            gap: 32px;
            align-items: center;
        }

        .nav-links a {
            color: var(--muted);
            text-decoration: none;
            font-weight: 500;
            padding-bottom: 8px;
            border-bottom: 2px solid transparent;
        }

        .nav-links a.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
            font-weight: 700;
        }

        .panel {
            background: var(--surface);
            border: 1px solid var(--outline);
            border-radius: 8px;
            padding: 24px;
        }

        .hero {
            min-height: 560px;
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(360px, 1fr);
            align-items: center;
            gap: 48px;
            border-bottom: 1px solid var(--outline);
            padding-bottom: 58px;
        }

        .hero h1 {
            font-size: 48px;
            line-height: 1.15;
            margin-bottom: 24px;
        }

        .hero p, .lead {
            color: var(--muted);
            font-size: 18px;
            line-height: 1.6;
        }

        .pipeline-row {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 28px;
            padding-top: 42px;
        }

        .step-number {
            width: 34px;
            height: 34px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border: 2px solid var(--primary);
            border-radius: 999px;
            color: var(--primary);
            background: #ffffff;
            font-weight: 700;
            margin-bottom: 14px;
        }

        .meta-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 16px;
            border: 1px solid var(--outline);
            border-radius: 8px;
            padding: 16px;
            background: #f9f9ff;
        }

        .meta-label {
            font-size: 11px;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
        }

        .mono {
            font-family: "JetBrains Mono", Consolas, monospace;
        }

        .error-box {
            border: 1px solid #f1a7a7;
            background: #fff7f7;
            border-radius: 8px;
            padding: 16px;
        }

        .algorithm-row {
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(320px, 520px);
            gap: 40px;
            align-items: center;
            border-bottom: 1px solid var(--outline);
            padding: 34px 0;
        }

        .algorithm-step {
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 12px;
            font-weight: 700;
        }

        div[data-testid="stButton"] > button,
        div[data-testid="stDownloadButton"] > button,
        [data-testid="stFileUploader"] button {
            background: #ffffff !important;
            color: var(--primary) !important;
            border-radius: 8px;
            border: 1px solid var(--primary);
            font-weight: 600;
            opacity: 1 !important;
        }

        div[data-testid="stButton"] > button *,
        div[data-testid="stDownloadButton"] > button *,
        [data-testid="stFileUploader"] button * {
            color: inherit !important;
        }

        div[data-testid="stButton"] > button[kind="primary"],
        div[data-testid="stDownloadButton"] > button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {
            background: var(--primary) !important;
            color: #ffffff !important;
            border-color: var(--primary) !important;
        }

        div[data-testid="stButton"] > button:hover,
        div[data-testid="stDownloadButton"] > button:hover,
        [data-testid="stFileUploader"] button:hover {
            background: #eef5ff !important;
            color: var(--primary) !important;
            border-color: var(--primary-hover) !important;
        }

        div[data-testid="stButton"] > button[kind="primary"]:hover,
        div[data-testid="stDownloadButton"] > button[kind="primary"]:hover,
        button[data-testid="stBaseButton-primary"]:hover {
            background: var(--primary-hover) !important;
            color: #ffffff !important;
            border-color: var(--primary-hover) !important;
        }

        div[data-testid="stButton"] > button:disabled,
        div[data-testid="stDownloadButton"] > button:disabled,
        [data-testid="stFileUploader"] button:disabled {
            background: #eef2f7 !important;
            color: #64748b !important;
            border-color: #cbd5e1 !important;
            opacity: 1 !important;
            cursor: not-allowed !important;
        }

        div[data-testid="stButton"] > button:disabled *,
        div[data-testid="stDownloadButton"] > button:disabled *,
        [data-testid="stFileUploader"] button:disabled * {
            color: #64748b !important;
        }

        div[data-baseweb="tab-list"] {
            gap: 22px;
            border-bottom: 1px solid var(--outline);
        }

        button[data-baseweb="tab"] {
            background: transparent;
            border-radius: 0;
            padding-left: 0;
            padding-right: 0;
            color: var(--muted) !important;
            font-weight: 600 !important;
            opacity: 1 !important;
        }

        button[data-baseweb="tab"] *,
        button[data-baseweb="tab"] p {
            color: inherit !important;
            font-weight: inherit !important;
            opacity: 1 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--primary) !important;
            border-bottom: 2px solid var(--primary) !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] *,
        button[data-baseweb="tab"][aria-selected="true"] p {
            color: var(--primary) !important;
            font-weight: 700 !important;
        }

        button[data-baseweb="tab"]:hover {
            color: var(--primary) !important;
            background: transparent !important;
        }

        @media (max-width: 900px) {
            .hero, .algorithm-row {
                grid-template-columns: 1fr;
            }
            .pipeline-row, .meta-grid {
                grid-template-columns: 1fr;
            }
            .nav-links {
                gap: 14px;
            }
            .hero h1 {
                font-size: 34px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
