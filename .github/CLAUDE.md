# Claude-specific guidance for agro_ia_app

When interacting with this repository as a Claude-style assistant, prefer the following:

- Be concise and structured: give short summaries, then a suggested small change.
- Prefer stepwise reasoning in private thoughts; surface only the final actionable steps.
- Avoid inventing missing files or undocumented behavior; ask the user instead.

Edit rules
- Use the repository's `apply_patch` format for code changes.
- When proposing code, include the smallest runnable patch and a one-line rationale.

Runtime notes
- The app is a Streamlit app: run with `streamlit run app.py` after installing `requirements.txt`.
- Models are stored in `models/`; treat them as large artifacts and do not re-upload them.
