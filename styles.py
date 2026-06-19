from __future__ import annotations

import streamlit as st


def apply_style() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1320px;
            padding-top: 1.1rem;
            padding-bottom: 2rem;
        }
        [data-testid="stMetric"] {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 14px 16px;
        }
        [data-testid="stMetricLabel"] {
            color: #475569;
        }
        [data-testid="stMetricValue"] {
            color: #0F172A;
            font-size: 1.75rem;
            line-height: 1.2;
            white-space: normal;
        }
        .stPlotlyChart {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 8px 10px 2px 10px;
            background: #FFFFFF;
        }
        .section-note {
            color: #64748B;
            font-size: 0.94rem;
            margin-top: -0.25rem;
            margin-bottom: 0.75rem;
        }
        .ai-card {
            min-height: 132px;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 6px solid var(--accent);
            border-radius: 8px;
            padding: 16px 18px;
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.06);
        }
        .ai-card h3 {
            margin: 0 0 0.5rem 0;
            font-size: 1.02rem;
            color: #0F172A;
        }
        .ai-card p {
            margin: 0;
            color: #475569;
            line-height: 1.65;
        }
        .ai-blue { --accent: #2563EB; }
        .ai-teal { --accent: #0F766E; }
        .ai-orange { --accent: #F59E0B; }
        .ai-purple { --accent: #7C3AED; }
        .ai-muted { --accent: #94A3B8; }
        .ai-output {
            background: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            padding: 18px 20px;
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.06);
        }
        .modebar {
            display: none !important;
        }
        button[kind="primary"] {
            border-radius: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
