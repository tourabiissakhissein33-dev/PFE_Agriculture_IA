# ══════════════════════════════════════════════════════════════════
# styles.py — CSS global partagé par toutes les pages
# ══════════════════════════════════════════════════════════════════

GLOBAL_CSS = """
<style>
/* ── Reset et base ── */
* { font-family: 'Segoe UI', sans-serif; }

/* ── Fond application ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #f0f4f0 0%, #e8f5e9 50%, #f0f4f8 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d3b5e 0%, #1a5276 60%, #1e8449 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebarNav"] a span,
[data-testid="stSidebarNav"] a {
    color: #ffffff !important;
    font-weight: 500;
}
[data-testid="stSidebarNav"] a {
    border-radius: 8px !important;
    margin: 2px 4px !important;
    padding: 6px 12px !important;
    transition: background .2s !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(255,255,255,0.15) !important;
}
[data-testid="stSidebarNav"] li.selected a,
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: rgba(255,255,255,0.25) !important;
    border-left: 3px solid #a9dfbf !important;
}

/* ── Header page ── */
.page-header {
    padding: 1rem 1.5rem;
    border-radius: 14px;
    margin-bottom: 1rem;
    color: white;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.page-header h1 {
    font-size: 1.6rem;
    font-weight: 800;
    margin: 0;
    line-height: 1.2;
}
.page-header p {
    font-size: 0.82rem;
    opacity: 0.9;
    margin: 0;
}

/* ── Cards ── */
.card {
    background: white;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
    border: 1px solid rgba(0,0,0,0.04);
}
.card-title {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #666;
    margin-bottom: 0.8rem;
}

/* ── Métriques ── */
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 0.9rem 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-bottom: 3px solid;
}
.metric-val {
    font-size: 1.7rem;
    font-weight: 800;
    line-height: 1;
}
.metric-lbl {
    font-size: 0.73rem;
    color: #777;
    margin-top: 4px;
    line-height: 1.3;
}

/* ── Status badges ── */
.status-ok {
    background: #e8f5e9;
    border: 1.5px solid #27ae60;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    font-size: 0.85rem;
    color: #1b5e20;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.8rem;
}
.status-warn {
    background: #fff3e0;
    border: 1.5px solid #ff9800;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    font-size: 0.85rem;
    color: #e65100;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.8rem;
}

/* ── Résultats ── */
.result-sain {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    border: 2px solid #27ae60;
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
    color: #1b5e20;
    font-size: 1.2rem;
    font-weight: 800;
    margin-bottom: 0.8rem;
}
.result-malade {
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    border: 2px solid #e53935;
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
    color: #b71c1c;
    font-size: 1.2rem;
    font-weight: 800;
    margin-bottom: 0.8rem;
}
.result-stress {
    background: linear-gradient(135deg, #fff8e1, #ffecb3);
    border: 2px solid #ffa000;
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
    color: #e65100;
    font-size: 1.2rem;
    font-weight: 800;
    margin-bottom: 0.8rem;
}
.result-irr {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    border: 2px solid #1565c0;
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
    color: #0d47a1;
    font-size: 1.2rem;
    font-weight: 800;
    margin-bottom: 0.8rem;
}
.result-no-irr {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    border: 2px solid #27ae60;
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
    color: #1b5e20;
    font-size: 1.2rem;
    font-weight: 800;
    margin-bottom: 0.8rem;
}

/* ── Conseil card ── */
.conseil {
    background: white;
    border-left: 4px solid #1565c0;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    font-size: 0.87rem;
    line-height: 1.6;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    margin-top: 0.6rem;
}

/* ── Météo box ── */
.meteo-box {
    background: white;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    border-left: 4px solid #1976d2;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
}
.meteo-title {
    font-size: 0.88rem;
    font-weight: 700;
    color: #1565c0;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── NDVI légende ── */
.ndvi-legend {
    display: flex;
    border-radius: 8px;
    overflow: hidden;
    height: 26px;
    font-size: 11px;
    font-weight: 700;
    color: white;
    margin: 6px 0 10px;
}
.nl-r { background: #e53935; flex: 2; display: flex; align-items: center; justify-content: center; }
.nl-y { background: #ff9800; flex: 2; display: flex; align-items: center; justify-content: center; }
.nl-g { background: #27ae60; flex: 3; display: flex; align-items: center; justify-content: center; }

/* ── Prob bar ── */
.prob-row { display: flex; align-items: center; gap: 8px; margin-bottom: 5px; font-size: 11px; }
.prob-bg { flex: 1; background: #f0f0f0; border-radius: 999px; height: 10px; overflow: hidden; }
.prob-fill { height: 100%; border-radius: 999px; }
.prob-val { width: 38px; text-align: right; font-weight: 600; font-size: 11px; }

/* ── Upload zone ── */
.upload-guide {
    background: #f8f9fa;
    border: 2px dashed #dee2e6;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    color: #666;
    font-size: 0.84rem;
    line-height: 1.6;
    margin-bottom: 0.8rem;
}

/* ── Info strips ── */
.info-strip {
    background: white;
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    font-size: 0.83rem;
}
.info-strip h4 {
    font-size: 0.88rem;
    color: #1a5276;
    margin: 0 0 0.45rem;
}
.info-strip li { margin-bottom: 3px; line-height: 1.4; color: #444; }

/* ── Tags ── */
.tag {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 999px;
    margin: 2px;
}

/* ── Footer ── */
.footer {
    text-align: center;
    font-size: 0.73rem;
    color: #999;
    border-top: 1px solid #e0e0e0;
    padding: 0.7rem;
    margin-top: 1.5rem;
}

/* ── Supprimer padding excessif Streamlit ── */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
}

/* ── Masquer hamburger Streamlit ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* ── Tables ── */
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
    margin: 6px 0;
}
.data-table th {
    background: #f5f5f5;
    padding: 5px 8px;
    text-align: left;
    font-weight: 600;
    font-size: 0.78rem;
    color: #555;
}
.data-table td {
    padding: 5px 8px;
    border-bottom: 1px solid #f0f0f0;
    line-height: 1.4;
}
.data-table tr:last-child td { border-bottom: none; }
</style>
"""
