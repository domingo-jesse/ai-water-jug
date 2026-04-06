from datetime import date, datetime

import pandas as pd
import streamlit as st

from config import APP_CONFIG, EstimationMode
from mock_llm import MockAssistant
from ui_components import (
    build_fun_fact,
    inject_base_styles,
    line_chart_data,
    render_jug,
    render_milestones,
    render_stats_card,
)
from utils import (
    estimate_tokens_from_text,
    make_session_summary,
    ml_to_liters,
    ml_to_ounces,
    safe_divide,
    summary_events_to_csv_bytes,
    summary_to_json_bytes,
)
from water_model import WaterEstimator


st.set_page_config(page_title="AI Water Jug", page_icon="💧", layout="wide")
inject_base_styles()


# --- Session bootstrap ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "events" not in st.session_state:
    st.session_state.events = []
if "session_total_ml" not in st.session_state:
    st.session_state.session_total_ml = 0.0
if "prompt_count" not in st.session_state:
    st.session_state.prompt_count = 0
if "assistant_word_total" not in st.session_state:
    st.session_state.assistant_word_total = 0
if "last_exchange_ml" not in st.session_state:
    st.session_state.last_exchange_ml = 0.0
if "milestones_seen" not in st.session_state:
    st.session_state.milestones_seen = set()
if "current_day" not in st.session_state:
    st.session_state.current_day = str(date.today())
if "daily_total_ml" not in st.session_state:
    st.session_state.daily_total_ml = 0.0
if "eco_streak" not in st.session_state:
    st.session_state.eco_streak = 0

if st.session_state.current_day != str(date.today()):
    st.session_state.current_day = str(date.today())
    st.session_state.daily_total_ml = 0.0

estimator = WaterEstimator()
assistant = MockAssistant()

# --- Top controls ---
st.title("AI Water Jug")
st.caption("See the estimated water footprint of your AI usage")

control_cols = st.columns([1.2, 1, 1, 1])
with control_cols[0]:
    mode = st.selectbox("Estimation mode", options=list(EstimationMode), format_func=lambda m: m.value)
with control_cols[1]:
    include_scope = st.toggle("Include indirect electricity water", value=True)
with control_cols[2]:
    daily_budget_ml = st.slider("Daily budget (mL)", min_value=100, max_value=3000, value=int(APP_CONFIG.default_daily_budget_ml), step=50)
with control_cols[3]:
    if st.button("Reset session", type="secondary"):
        for key in [
            "messages",
            "events",
            "session_total_ml",
            "prompt_count",
            "assistant_word_total",
            "last_exchange_ml",
            "milestones_seen",
            "daily_total_ml",
            "eco_streak",
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

custom_ml_per_1k = APP_CONFIG.mode_defaults[EstimationMode.MEDIUM].ml_per_1k_tokens
custom_include_indirect = include_scope
bottle_size_ml = APP_CONFIG.default_bottle_size_ml

if mode == EstimationMode.CUSTOM:
    custom_cols = st.columns(3)
    with custom_cols[0]:
        custom_ml_per_1k = st.number_input(
            "Custom mL per 1,000 tokens",
            min_value=0.0,
            value=5.0,
            step=0.1,
            help="Set your own assumption for water intensity.",
        )
    with custom_cols[1]:
        custom_include_indirect = st.toggle("Custom includes indirect", value=True)
    with custom_cols[2]:
        bottle_size_ml = st.number_input(
            "Bottle size (mL)", min_value=100, max_value=2000, value=500, step=50
        )

main_col, side_col = st.columns([1.7, 1.0], gap="large")

# --- Left: chat ---
with main_col:
    st.subheader("Chat")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("exchange_ml") is not None:
                st.markdown(
                    f"<div class='assist-note'>Estimated water for this exchange: {message['exchange_ml']:.2f} mL</div>",
                    unsafe_allow_html=True,
                )

    prompt = st.chat_input("Send a message to the assistant")

    action_cols = st.columns([1, 1, 3])
    with action_cols[0]:
        clear_chat = st.button("Clear conversation")
    with action_cols[1]:
        send_clicked = st.button("Send", type="primary")

    if clear_chat:
        st.session_state.messages = []
        st.session_state.events = []
        st.session_state.prompt_count = 0
        st.session_state.assistant_word_total = 0
        st.session_state.session_total_ml = 0.0
        st.session_state.daily_total_ml = 0.0
        st.session_state.last_exchange_ml = 0.0
        st.session_state.milestones_seen = set()
        st.rerun()

    should_send = bool(prompt) or (send_clicked and bool(prompt))
    if should_send:
        user_message = prompt.strip()
        st.session_state.messages.append({"role": "user", "content": user_message})

        assistant_reply = assistant.generate(user_message, st.session_state.prompt_count)

        user_tokens = estimate_tokens_from_text(user_message)
        assistant_tokens = estimate_tokens_from_text(assistant_reply)

        estimate = estimator.estimate_exchange(
            user_tokens=user_tokens,
            assistant_tokens=assistant_tokens,
            mode=mode,
            include_indirect_toggle=include_scope,
            custom_ml_per_1k_tokens=custom_ml_per_1k,
            custom_include_indirect=custom_include_indirect,
        )

        st.session_state.last_exchange_ml = estimate.final_ml
        st.session_state.session_total_ml += estimate.final_ml
        st.session_state.daily_total_ml += estimate.final_ml
        st.session_state.prompt_count += 1
        st.session_state.assistant_word_total += len(assistant_reply.split())

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_reply,
                "exchange_ml": estimate.final_ml,
            }
        )

        st.session_state.events.append(
            {
                "index": st.session_state.prompt_count,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "user_tokens": estimate.user_tokens,
                "assistant_tokens": estimate.assistant_tokens,
                "total_tokens": estimate.total_tokens,
                "water_ml": round(estimate.final_ml, 4),
                "mode": estimate.mode,
                "include_indirect": estimate.include_indirect,
            }
        )
        st.rerun()

# --- Right: jug + stats ---
with side_col:
    st.subheader("Water meter")
    fill_ratio = st.session_state.session_total_ml / APP_CONFIG.jug_capacity_ml
    render_jug(fill_ratio, st.session_state.session_total_ml, APP_CONFIG.jug_capacity_ml)

    liters = ml_to_liters(st.session_state.session_total_ml)
    ounces = ml_to_ounces(st.session_state.session_total_ml)
    bottles = safe_divide(st.session_state.session_total_ml, bottle_size_ml)

    render_stats_card("This message estimate", f"{st.session_state.last_exchange_ml:.2f} mL")
    render_stats_card("Session total", f"{st.session_state.session_total_ml:.2f} mL")
    render_stats_card("Daily budget", f"{daily_budget_ml:.0f} mL")

    mini1, mini2 = st.columns(2)
    with mini1:
        render_stats_card("Prompts sent", str(st.session_state.prompt_count))
        render_stats_card(
            "Avg water / prompt",
            f"{safe_divide(st.session_state.session_total_ml, max(st.session_state.prompt_count, 1)):.2f} mL",
        )
    with mini2:
        render_stats_card("Assistant words", str(st.session_state.assistant_word_total))
        render_stats_card("Mode", mode.value)

    st.markdown(
        f"**Totals:** {st.session_state.session_total_ml:.2f} mL · {liters:.3f} L · {ounces:.2f} oz · {bottles:.2f} bottles"
    )

    milestone_hits = []
    if bottles >= 1 and "bottle" not in st.session_state.milestones_seen:
        milestone_hits.append("1 bottle used")
        st.session_state.milestones_seen.add("bottle")
    if liters >= 1 and "liter" not in st.session_state.milestones_seen:
        milestone_hits.append("1 liter used")
        st.session_state.milestones_seen.add("liter")
    if st.session_state.daily_total_ml > daily_budget_ml and "budget" not in st.session_state.milestones_seen:
        milestone_hits.append("Daily budget exceeded")
        st.session_state.milestones_seen.add("budget")

    render_milestones(milestone_hits)

    if st.session_state.daily_total_ml <= daily_budget_ml and st.session_state.prompt_count > 0:
        st.session_state.eco_streak += 1
    elif st.session_state.daily_total_ml > daily_budget_ml:
        st.session_state.eco_streak = 0

    st.success(f"Eco streak: {st.session_state.eco_streak} check-ins under budget 🌱")

    if st.session_state.prompt_count > 0 and st.session_state.prompt_count % 3 == 0:
        st.caption(f"Fun fact: {build_fun_fact(st.session_state.prompt_count)}")

# --- Chart + downloads + educational notes ---
if st.session_state.events:
    st.subheader("Usage over prompts")
    chart_df = pd.DataFrame(line_chart_data(st.session_state.events))
    st.line_chart(chart_df, x="Prompt", y="Water (mL)", use_container_width=True)

assumptions = estimator.resolve_assumptions(
    mode,
    include_scope,
    custom_ml_per_1k,
    custom_include_indirect,
)
summary = make_session_summary(
    messages=st.session_state.messages,
    events=st.session_state.events,
    totals={
        "session_total_ml": round(st.session_state.session_total_ml, 4),
        "daily_total_ml": round(st.session_state.daily_total_ml, 4),
        "prompt_count": st.session_state.prompt_count,
        "assistant_word_total": st.session_state.assistant_word_total,
    },
    assumptions={
        **assumptions,
        "bottle_size_ml": bottle_size_ml,
        "mode": mode.value,
    },
)

export_cols = st.columns(2)
with export_cols[0]:
    st.download_button(
        label="Download session JSON",
        file_name="ai-water-jug-session.json",
        mime="application/json",
        data=summary_to_json_bytes(summary),
        use_container_width=True,
    )
with export_cols[1]:
    st.download_button(
        label="Download events CSV",
        file_name="ai-water-jug-events.csv",
        mime="text/csv",
        data=summary_events_to_csv_bytes(st.session_state.events),
        use_container_width=True,
    )

with st.expander("How this estimate works"):
    st.markdown(
        """
- This app shows **estimated** water usage, not exact measurements.
- Estimates can vary significantly by model, data center location, cooling system, and accounting method.
- Water use may include direct cooling plus indirect impacts from electricity generation.
- The goal is awareness and reflection, not precise metering.
        """
    )

st.caption(
    "Method note: token-based water estimates rely on simplified assumptions and should be interpreted as directional ranges."
)
