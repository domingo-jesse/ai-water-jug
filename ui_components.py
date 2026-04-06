from typing import Dict, List

import streamlit as st


def inject_base_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }
        .app-card {
            border: 1px solid rgba(255, 255, 255, 0.12);
            background: rgba(255, 255, 255, 0.03);
            border-radius: 16px;
            padding: 14px;
            margin-bottom: 10px;
        }
        .metric-label {
            color: #b3bfd1;
            font-size: 0.8rem;
            margin-bottom: 3px;
        }
        .metric-value {
            font-size: 1.25rem;
            font-weight: 700;
        }
        .jug-shell {
            width: 100%;
            max-width: 240px;
            height: 360px;
            border-radius: 20px 20px 28px 28px;
            border: 3px solid rgba(149, 186, 255, 0.8);
            margin: 0 auto 12px auto;
            position: relative;
            overflow: hidden;
            background: linear-gradient(180deg, rgba(45, 56, 72, 0.35), rgba(17, 24, 39, 0.5));
            box-shadow: inset 0 0 24px rgba(100, 132, 255, 0.2);
        }
        .jug-water {
            position: absolute;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(180deg, rgba(67, 153, 255, 0.75), rgba(42, 112, 255, 0.95));
            transition: height 0.6s ease;
        }
        .jug-wave {
            position: absolute;
            top: -12px;
            left: -10%;
            width: 120%;
            height: 20px;
            border-radius: 40%;
            background: rgba(178, 226, 255, 0.35);
            animation: drift 4s linear infinite;
        }
        @keyframes drift {
            from { transform: translateX(-10px); }
            to { transform: translateX(10px); }
        }
        .assist-note {
            color: #9ec8ff;
            font-size: 0.86rem;
            margin-top: 4px;
            margin-bottom: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_jug(fill_ratio: float, total_ml: float, capacity_ml: float) -> None:
    fill_percent = max(0.0, min(fill_ratio * 100, 100.0))
    st.markdown(
        f"""
        <div class="jug-shell" aria-label="Water jug visualization">
            <div class="jug-water" style="height: {fill_percent:.2f}%">
                <div class="jug-wave"></div>
            </div>
        </div>
        <div style="text-align:center;color:#b7d3ff;font-size:0.92rem;">
            {total_ml:.1f} mL / {capacity_ml:.0f} mL visual capacity
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats_card(title: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="app-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_milestones(milestones: List[str]) -> None:
    if not milestones:
        return
    joined = " ".join([f"🏅 {item}" for item in milestones])
    st.info(joined)


def build_fun_fact(prompt_count: int) -> str:
    facts = [
        "Cooling strategies can change data center water usage patterns significantly.",
        "Indirect water use depends heavily on local electricity generation mix.",
        "Better prompts can reduce back-and-forth and potentially lower estimated impact.",
        "Comparative tools are best used for awareness, not exact accounting.",
    ]
    return facts[prompt_count % len(facts)]


def line_chart_data(events: List[Dict]) -> List[Dict]:
    return [
        {"Prompt": i + 1, "Water (mL)": event["water_ml"]}
        for i, event in enumerate(events)
    ]
