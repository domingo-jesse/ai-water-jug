# AI Water Jug

AI Water Jug is a playful Streamlit MVP that simulates a chat interface and visualizes the **estimated** water footprint of each AI exchange.

> Important: estimates are heuristic only. The app is designed for awareness, not precise measurement.

## Features

- Chat interface with mock assistant responses (default mode)
- Water estimation modes: Conservative, Medium, High, Custom
- Scope toggle: direct cooling only vs direct + indirect electricity-related water
- Animated water jug meter that fills as session usage grows
- Per-message and session totals in mL, liters, ounces, and bottle equivalents
- Prompt-level line chart and milestone badges
- Daily budget slider + eco streak indicator
- Export session summary as JSON and prompt events as CSV
- Educational explainer panel: "How this estimate works"

## Project structure

- `app.py` – Streamlit app entrypoint and page composition
- `config.py` – estimation defaults and global config dataclasses
- `water_model.py` – transparent estimation logic
- `mock_llm.py` – local mock assistant behavior
- `ui_components.py` – reusable UI/CSS components
- `utils.py` – token helpers, conversion helpers, and export utilities

## Quickstart

### 1. Create a virtual environment (optional but recommended)

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run locally

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit (usually `http://localhost:8501`).

## Estimation methodology (default assumptions)

Token estimate helper:

- `rough_tokens = ceil(characters / 4)`

Water intensity defaults (mL per 1,000 tokens):

- Conservative: `0.5`
- Medium: `5.0`
- High: `25.0`

Indirect water inclusion:

- When enabled, app multiplies base estimate by `indirect_multiplier` (`1.6` by default).

All values are editable in `config.py`.

## Using custom mode

Custom mode allows users to specify:

- mL per 1,000 tokens
- whether indirect electricity water is included
- bottle size used for conversion cards

## Swapping mock assistant for OpenAI API later

The default assistant is in `mock_llm.py`.

To integrate OpenAI later:

1. Create a real assistant client module (e.g. `openai_llm.py`) with a `generate(user_message, turn_index)` method.
2. Replace `assistant = MockAssistant()` in `app.py` with your OpenAI-backed implementation.
3. Keep the same interface so estimation logic remains unchanged.
4. Add required package(s) to `requirements.txt` and configure secrets with `.streamlit/secrets.toml` or Streamlit Cloud secrets.

## Deployment notes

This project is Streamlit deployment-ready:

- main entrypoint: `app.py`
- dependencies: `requirements.txt`

Deploy directly to Streamlit Community Cloud by connecting the repo and selecting `app.py`.
