import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from styles import GLOBAL_CSS

st.set_page_config(
    page_title="Agro-IA Tchad",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── HERO ─────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#0d3b5e,#27ae60);
     border-radius:16px;padding:1.8rem 2rem;color:white;
     text-align:center;margin-bottom:1.2rem">
  <div style="font-size:2rem;font-weight:900;letter-spacing:-1px;
       margin-bottom:4px">🌾 Agro-IA Tchad</div>
  <div style="font-size:0.92rem;opacity:0.92">
    Cadre décisionnel basé sur l'Intelligence Artificielle
    pour l'optimisation du suivi parcellaire agricole
  </div>
</div>""", unsafe_allow_html=True)

# ── MÉTRIQUES ────────────────────────────────────────────────────
c1,c2,c3,c4 = st.columns(4)
for col,val,lbl,clr,bc in [
    (c1,"78.51%","💧 Irrigation\nRandom Forest","#1565c0","#1565c0"),
    (c2,"95.42%","🌿 Fertilisation\nXGBoost","#27ae60","#27ae60"),
    (c3,"96.61%","🔬 Maladies CNN\nMobileNetV2","#e65100","#e65100"),
    (c4,"5 cultures","🌾 Cultures\nTchad","#6a1b9a","#6a1b9a"),
]:
    col.markdown(
        f'<div class="metric-card" style="border-color:{bc}">'
        f'<div class="metric-val" style="color:{clr}">{val}</div>'
        f'<div class="metric-lbl">{lbl}</div></div>',
        unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CARTES MODULES ────────────────────────────────────────────────
m1,m2,m3 = st.columns(3, gap="medium")
CARDS = [
    ("💧","Module Irrigation","#1565c0",
     "Prédit le besoin en eau d'une parcelle à partir des données climatiques <b>temps réel</b> (Open-Meteo) et des paramètres agronomiques du sol.",
     ["Random Forest","78.51%","AUC 0.878","🛰️ Météo temps réel"]),
    ("🌿","Module Fertilisation","#27ae60",
     "Recommande le type d'engrais optimal selon l'analyse <b>NPK du sol</b>, la culture, le type de sol et les conditions climatiques.",
     ["XGBoost","95.42%","F1 95.47%","DAP · Urée · NPK"]),
    ("🔬","Module Maladies","#e65100",
     "Détecte les maladies via <b>photo CNN</b> ou <b>indices NDVI drone/satellite</b> avec météo temps réel — approche hybride unique.",
     ["MobileNetV2","96.61%","📸 Photo CNN","🛰️ NDVI Drone"]),
]
for col,(ic,ti,cl,desc,tags) in zip([m1,m2,m3],CARDS):
    tags_html = "".join(
        f'<span class="tag" style="background:#f0f4f0;color:{cl};'
        f'border:1px solid {cl}20">{t}</span>' for t in tags)
    col.markdown(
        f'<div class="card" style="border-top:4px solid {cl};min-height:200px">'
        f'<div style="font-size:1.8rem;margin-bottom:0.4rem">{ic}</div>'
        f'<div style="font-size:1rem;font-weight:700;color:{cl};margin-bottom:0.5rem">{ti}</div>'
        f'<div style="font-size:0.83rem;color:#555;line-height:1.5;margin-bottom:0.7rem">{desc}</div>'
        f'{tags_html}</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CONTEXTE ─────────────────────────────────────────────────────
ca,cb,cc = st.columns(3, gap="medium")
ca.markdown("""<div class="info-strip"><h4>🌾 Cultures couvertes</h4><ul>
<li>Mil <em>(Pennisetum glaucum)</em></li>
<li>Sorgho <em>(Sorghum bicolor)</em></li>
<li>Arachide <em>(Arachis hypogaea)</em></li>
<li>Maïs <em>(Zea mays)</em></li>
<li>Coton <em>(Gossypium hirsutum)</em></li>
</ul></div>""", unsafe_allow_html=True)

cb.markdown("""<div class="info-strip"><h4>🗺️ Zones géographiques</h4><ul>
<li>🏙️ N'Djamena <em>(Sahélienne)</em></li>
<li>🏙️ Abéché <em>(Sahélienne)</em></li>
<li>🌿 Sarh <em>(Soudanienne)</em></li>
<li>🌿 Moundou <em>(Soudanienne)</em></li>
<li>🌿 Bongor <em>(Soudanienne)</em></li>
</ul></div>""", unsafe_allow_html=True)

cc.markdown("""<div class="info-strip"><h4>📡 Sources de données</h4><ul>
<li>🛰️ <b>Open-Meteo</b> — météo temps réel</li>
<li>🚀 NASA POWER — entraînement 2015–2023</li>
<li>🖼️ PlantVillage — images maladies</li>
<li>🌽 Dataset local tchadien</li>
</ul></div>""", unsafe_allow_html=True)

st.markdown("""
<div style="background:linear-gradient(90deg,#0d47a1,#1976d2);
     color:white;border-radius:12px;padding:0.8rem 1.2rem;
     font-size:0.85rem;margin-top:0.8rem;display:flex;
     align-items:center;gap:10px">
  🛰️ <b>Météo temps réel</b> — Open-Meteo API intégrée dans les modules
  Irrigation et Maladies pour pré-remplir automatiquement les données
  climatiques des 5 villes tchadiennes.
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.info("👈 Utilisez le **menu de gauche** pour accéder aux 3 modules.")

st.markdown("""<div class="footer">
PFE Licence 3 Informatique — ENASTIC 2025/2026 &nbsp;|&nbsp;
TOURABI ISSAK HISSEIN &nbsp;|&nbsp; Dr. MOUAZ MIKAIL
</div>""", unsafe_allow_html=True)
