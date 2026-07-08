# Agent Guidance for agro_ia_app

Purpose: concise, actionable instructions so coding assistants (Copilot/Claude/etc.) can be productive quickly.

Quick start
- Install: `pip install -r requirements.txt`
- Run locally: `streamlit run app.py`

Key facts for agents
- Entry point: [app.py](app.py#L1)
- UI pages: [pages/1_💧_Irrigation.py](pages/1_💧_Irrigation.py#L1), [pages/2_🌿_Fertilisation.py](pages/2_🌿_Fertilisation.py#L1), [pages/3_🔬_Detection_Maladies.py](pages/3_🔬_Detection_Maladies.py#L1)
- Models directory: [models/](models/)
- Streamlit config: [.streamlit/config.toml](.streamlit/config.toml#L1)

Conventions and constraints
- Use `apply_patch` edits for code changes; keep edits minimal and focused.
- Avoid adding or committing large model binaries in the repo.
- Ask clarifying questions before changing model weights or inference code.

Where to look for more info
- Project README: [README.md](README.md#L1)
