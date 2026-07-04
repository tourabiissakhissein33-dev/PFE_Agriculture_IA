# styles.py — CSS global partagé — Version finale corrigée

GLOBAL_CSS = """
<style>
* { font-family: 'Segoe UI', Arial, sans-serif; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg,#f0f4f0 0%,#e8f5e9 50%,#f0f4f8 100%) !important;
}
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0d3b5e 0%,#1a5276 55%,#1e6b3a 100%) !important;
}
[data-testid="stSidebar"] * { color:#ffffff !important; }
[data-testid="stSidebar"] a {
    color:#ffffff !important; font-weight:500;
    text-decoration:none; border-radius:8px;
    padding:4px 8px; display:block;
}
[data-testid="stSidebar"] a:hover { background:rgba(255,255,255,0.18) !important; }
[data-testid="stSidebar"] [aria-current="page"] {
    background:rgba(255,255,255,0.25) !important;
    border-left:3px solid #a9dfbf !important;
}
.block-container { padding-top:1.2rem !important; padding-bottom:1rem !important; }
.page-header {
    padding:1rem 1.5rem; border-radius:14px; margin-bottom:1rem;
    color:white; display:flex; align-items:center; gap:1rem;
}
.page-header h1 { font-size:1.6rem; font-weight:800; margin:0; }
.page-header p  { font-size:0.82rem; opacity:0.9; margin:0; }
.card {
    background:white; border-radius:14px; padding:1.2rem 1.4rem;
    box-shadow:0 2px 12px rgba(0,0,0,0.07); margin-bottom:1rem;
    border:1px solid rgba(0,0,0,0.04);
}
.card-title {
    font-size:0.8rem; font-weight:600; text-transform:uppercase;
    letter-spacing:0.05em; color:#666; margin-bottom:0.8rem;
}
.metric-card {
    background:white; border-radius:12px; padding:0.9rem 1rem;
    text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.07);
    border-bottom:3px solid; margin-bottom:0.5rem;
}
.metric-val { font-size:1.7rem; font-weight:800; line-height:1; }
.metric-lbl { font-size:0.73rem; color:#777; margin-top:4px; line-height:1.3; }
.status-ok {
    background:#e8f5e9; border:1.5px solid #27ae60; border-radius:10px;
    padding:0.6rem 1rem; font-size:0.85rem; color:#1b5e20; font-weight:600;
    margin-bottom:0.8rem;
}
.status-warn {
    background:#fff3e0; border:1.5px solid #ff9800; border-radius:10px;
    padding:0.6rem 1rem; font-size:0.85rem; color:#e65100; font-weight:600;
    margin-bottom:0.8rem;
}
.meteo-box {
    background:white; border-radius:12px; padding:1rem 1.2rem;
    border-left:4px solid #1976d2; box-shadow:0 2px 10px rgba(0,0,0,0.06);
    margin-bottom:1rem;
}
.meteo-title { font-size:0.88rem; font-weight:700; color:#1565c0; margin-bottom:0.6rem; }
.result-sain {
    background:linear-gradient(135deg,#e8f5e9,#c8e6c9); border:2px solid #27ae60;
    border-radius:14px; padding:1.2rem; text-align:center;
    color:#1b5e20; font-size:1.2rem; font-weight:800; margin-bottom:0.8rem;
}
.result-malade {
    background:linear-gradient(135deg,#ffebee,#ffcdd2); border:2px solid #e53935;
    border-radius:14px; padding:1.2rem; text-align:center;
    color:#b71c1c; font-size:1.2rem; font-weight:800; margin-bottom:0.8rem;
}
.result-stress {
    background:linear-gradient(135deg,#fff8e1,#ffecb3); border:2px solid #ffa000;
    border-radius:14px; padding:1.2rem; text-align:center;
    color:#e65100; font-size:1.2rem; font-weight:800; margin-bottom:0.8rem;
}
.result-irr {
    background:linear-gradient(135deg,#e3f2fd,#bbdefb); border:2px solid #1565c0;
    border-radius:14px; padding:1.2rem; text-align:center;
    color:#0d47a1; font-size:1.2rem; font-weight:800; margin-bottom:0.8rem;
}
.result-no-irr {
    background:linear-gradient(135deg,#e8f5e9,#c8e6c9); border:2px solid #27ae60;
    border-radius:14px; padding:1.2rem; text-align:center;
    color:#1b5e20; font-size:1.2rem; font-weight:800; margin-bottom:0.8rem;
}
.conseil {
    background:white; border-left:4px solid #1565c0; border-radius:10px;
    padding:0.9rem 1.1rem; font-size:0.87rem; line-height:1.6;
    box-shadow:0 2px 6px rgba(0,0,0,0.05); margin-top:0.6rem;
}
.upload-guide {
    background:#f8f9fa; border:2px dashed #dee2e6; border-radius:12px;
    padding:1.2rem; text-align:center; color:#555;
    font-size:0.84rem; line-height:1.7; margin-bottom:0.8rem;
}
.ndvi-legend {
    display:flex; border-radius:8px; overflow:hidden; height:26px;
    font-size:11px; font-weight:700; color:white; margin:6px 0 10px;
}
.nl-r{background:#e53935;flex:2;display:flex;align-items:center;justify-content:center}
.nl-y{background:#ff9800;flex:2;display:flex;align-items:center;justify-content:center}
.nl-g{background:#27ae60;flex:3;display:flex;align-items:center;justify-content:center}
.prob-row{display:flex;align-items:center;gap:8px;margin-bottom:5px;font-size:11px}
.prob-bg{flex:1;background:#f0f0f0;border-radius:999px;height:10px;overflow:hidden}
.prob-fill{height:100%;border-radius:999px}
.prob-val{width:38px;text-align:right;font-weight:600;font-size:11px}
.info-strip {
    background:white; border-radius:12px; padding:0.9rem 1.1rem;
    box-shadow:0 2px 8px rgba(0,0,0,0.05); font-size:0.83rem; margin-bottom:0.8rem;
}
.info-strip h4 { font-size:0.88rem; color:#1a5276; margin:0 0 0.45rem; font-weight:600; }
.info-strip li { margin-bottom:3px; line-height:1.4; color:#444; }
.tag {
    display:inline-block; font-size:0.72rem; font-weight:600;
    padding:2px 8px; border-radius:999px; margin:2px;
}
.drone-card { border-radius:12px; padding:1rem 1.3rem; margin-bottom:0.8rem; font-size:0.84rem; line-height:1.7; }
.hist-row {
    background:white; border-radius:10px; padding:0.8rem 1rem;
    margin-bottom:0.5rem; border-left:4px solid #ccc;
    box-shadow:0 1px 6px rgba(0,0,0,0.05); display:flex;
    align-items:center; justify-content:space-between; font-size:0.85rem;
}
.hist-irr{border-color:#1565c0} .hist-fert{border-color:#27ae60} .hist-mal{border-color:#e65100}
.footer {
    text-align:center; font-size:0.73rem; color:#999;
    border-top:1px solid #e0e0e0; padding:0.7rem; margin-top:1rem;
}
#MainMenu{visibility:hidden} footer{visibility:hidden}
[data-testid="stDecoration"]{display:none}
</style>
"""
