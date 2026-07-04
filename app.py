import streamlit as st
import sys, os
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path: sys.path.insert(0, ROOT)
from styles   import GLOBAL_CSS
from database import initialiser_db, statistiques

st.set_page_config(page_title="Agro-IA Tchad",page_icon="🌾",
                   layout="wide",initial_sidebar_state="expanded")
initialiser_db()
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

st.markdown("""
<div style="background:linear-gradient(135deg,#0d3b5e,#27ae60);
     border-radius:16px;padding:1.8rem 2rem;color:white;
     text-align:center;margin-bottom:1.2rem">
  <div style="font-size:2rem;font-weight:900;margin-bottom:4px">🌾 Agro-IA Tchad</div>
  <div style="font-size:0.92rem;opacity:0.92">
    Cadre décisionnel basé sur l'IA pour l'optimisation du suivi
    parcellaire agricole au Tchad — avec historique SQLite
  </div>
</div>""", unsafe_allow_html=True)

# Métriques IA avec vraies valeurs
c1,c2,c3,c4 = st.columns(4)
for col,val,lbl,clr in [
    (c1,"78.51%","💧 Irrigation\nRandom Forest · AUC 0.878","#1565c0"),
    (c2,"95.42%","🌿 Fertilisation\nXGBoost · F1 95.47%","#27ae60"),
    (c3,"52.27%","🔬 Maladies CNN\nMobileNetV2 · 287 images","#e65100"),
    (c4,"5 cultures","🌾 Mil·Sorgho·Arachide\nMaïs·Coton","#6a1b9a"),
]:
    col.markdown(
        f'<div class="metric-card" style="border-color:{clr}">'
        f'<div class="metric-val" style="color:{clr}">{val}</div>'
        f'<div class="metric-lbl">{lbl}</div></div>',
        unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Stats SQLite
try:
    stats = statistiques()
    if stats["total"] > 0:
        st.markdown("### 📊 Historique des analyses")
        s1,s2,s3,s4 = st.columns(4)
        s1.metric("📋 Total",stats["total"])
        s2.metric("💧 Irrigation",stats["n_irrigation"])
        s3.metric("🌿 Fertilisation",stats["n_fertilisation"])
        s4.metric("🔬 Maladies",stats["n_maladies"])
        if stats["total"]>0:
            ss1,ss2,ss3,ss4=st.columns(4)
            ss1.metric("🌾 Culture + analysée",stats["top_culture"])
            ss2.metric("📍 Zone à risque",stats["zone_risque"])
            ss3.metric("💧 Taux irrigation",f"{stats['taux_irrigation']}%")
            ss4.metric("🦠 Taux maladies",f"{stats['taux_maladie']}%")
        st.markdown("<br>", unsafe_allow_html=True)
except Exception:
    pass

# Cartes modules
m1,m2,m3 = st.columns(3,gap="medium")
CARDS = [
    ("💧","Module Irrigation","#1565c0",
     "Prédit le besoin en eau via Random Forest entraîné sur <b>16 435 observations NASA POWER</b> réelles (2015–2023). Météo Open-Meteo temps réel.",
     ["Random Forest","78.51% Accuracy","AUC-ROC 0.878","F1 72.57%","CV 78.87%","🛰️ Météo temps réel","💾 SQLite"]),
    ("🌿","Module Fertilisation","#27ae60",
     "Recommande l'engrais optimal via XGBoost entraîné sur <b>1 599 observations</b> (Kaggle réel + augmentation). Variable clé : Phosphore P (0.44).",
     ["XGBoost","95.42% Accuracy","F1 95.47%","CV 97.23%","P→N→K priorité","💾 SQLite"]),
    ("🔬","Module Maladies","#e65100",
     "CNN MobileNetV2 entraîné sur <b>287 images tchadiennes réelles</b>. Méthodes : Photo CNN + NDVI Sentinel-2 auto + Caméra smartphone.",
     ["MobileNetV2","52.27% Accuracy","📸 CNN Photo","🛰️ Sentinel-2","📷 Caméra VARI","💾 SQLite"]),
]
for col,(ic,ti,cl,desc,tags) in zip([m1,m2,m3],CARDS):
    tags_html="".join(f'<span class="tag" style="background:#f0f4f0;color:{cl};border:1px solid {cl}30">{t}</span>' for t in tags)
    col.markdown(
        f'<div class="card" style="border-top:4px solid {cl};min-height:220px">'
        f'<div style="font-size:1.8rem;margin-bottom:.4rem">{ic}</div>'
        f'<div style="font-size:1rem;font-weight:700;color:{cl};margin-bottom:.5rem">{ti}</div>'
        f'<div style="font-size:.83rem;color:#555;line-height:1.5;margin-bottom:.7rem">{desc}</div>'
        f'{tags_html}</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
ca,cb,cc=st.columns(3,gap="medium")
ca.markdown("""<div class="info-strip"><h4>🌾 Cultures couvertes</h4><ul>
<li>Mil <em>(Pennisetum glaucum)</em></li>
<li>Sorgho <em>(Sorghum bicolor)</em></li>
<li>Arachide <em>(Arachis hypogaea)</em></li>
<li>Maïs <em>(Zea mays)</em></li>
<li>Coton <em>(Gossypium hirsutum)</em></li></ul></div>""",unsafe_allow_html=True)
cb.markdown("""<div class="info-strip"><h4>🗺️ Zones géographiques</h4><ul>
<li>🏙️ N'Djamena <em>(Sahélienne)</em></li>
<li>🏙️ Abéché <em>(Sahélienne)</em></li>
<li>🌿 Sarh <em>(Soudanienne)</em></li>
<li>🌿 Moundou <em>(Soudanienne)</em></li>
<li>🌿 Bongor <em>(Soudanienne)</em></li></ul></div>""",unsafe_allow_html=True)
cc.markdown("""<div class="info-strip"><h4>📊 Données d'entraînement</h4><ul>
<li>💧 Irrigation : NASA POWER 16 435 obs.</li>
<li>🌿 Fertilisation : 1 599 obs. (Kaggle+Aug.)</li>
<li>🔬 Maladies : 287 images tchadiennes</li>
<li>🛰️ Open-Meteo API — météo temps réel</li>
<li>🗄️ SQLite — historique local</li></ul></div>""",unsafe_allow_html=True)

st.info("👈 Utilisez le **menu de gauche** pour accéder aux 4 modules · **📋 Historique** pour voir toutes les analyses.")
st.markdown("""<div class="footer">PFE Licence 3 Informatique — ENASTIC 2025/2026 &nbsp;|&nbsp;
TOURABI ISSAK HISSEIN &nbsp;|&nbsp; Dr. MOUAZ MIKAIL</div>""",unsafe_allow_html=True)
