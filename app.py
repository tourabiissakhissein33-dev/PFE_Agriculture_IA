# ╔══════════════════════════════════════════════════════════════════╗
# ║  AGRO-IA TCHAD — Application Streamlit                         ║
# ║  Cadre décisionnel IA pour l'agriculture tchadienne            ║
# ║  Étudiant : TOURABI ISSAK HISSEIN — ENASTIC 2025/2026          ║
# ╚══════════════════════════════════════════════════════════════════╝

import streamlit as st
import sys, os

st.set_page_config(
    page_title="Agro-IA Tchad",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
.main-title {
    font-size:2.2rem; font-weight:700;
    color:#1a5276; text-align:center; margin-bottom:0.3rem;
}
.sub-title {
    font-size:1.1rem; color:#5d6d7e;
    text-align:center; margin-bottom:2rem;
}
.module-card {
    background:#f8f9fa; border-left:4px solid #1a5276;
    border-radius:8px; padding:1.2rem; margin-bottom:1rem;
}
.result-ok     { background:#e8f5e9; border-left:4px solid #27ae60;
                 border-radius:8px; padding:1rem; font-weight:600; }
.result-danger { background:#fce4e4; border-left:4px solid #e74c3c;
                 border-radius:8px; padding:1rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Titre ─────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🌾 Agro-IA Tchad</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Cadre décisionnel basé sur l\'IA '
    'pour l\'optimisation du suivi parcellaire</div>',
    unsafe_allow_html=True)

st.divider()

# ── Métriques de performance ──────────────────────────────────────
st.subheader("🏆 Performances des modules IA")
c1, c2, c3 = st.columns(3)
c1.metric("💧 Irrigation — Accuracy",  "78.51%",  "AUC-ROC : 0.878")
c2.metric("🌿 Fertilisation — Accuracy","95.42%", "F1 : 95.47%")
c3.metric("🔬 Maladies — Val Accuracy", "96.61%", "CNN Phase 1")

st.divider()

# ── Cartes des modules ────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
<div class="module-card">
    <h3 style="color:#1565c0">💧 Module Irrigation</h3>
    <p>Prédit le besoin en eau d'une parcelle à partir des données
    climatiques <b>en temps réel</b> (Open-Meteo) et du sol.</p>
    <p><b>Algorithme :</b> Random Forest<br>
    <b>Accuracy :</b> 78.51% | AUC-ROC : 0.878<br>
    <b>Données météo :</b> 🛰️ Open-Meteo (temps réel)</p>
</div>""", unsafe_allow_html=True)

with col2:
    st.markdown("""
<div class="module-card">
    <h3 style="color:#1b5e20">🌿 Module Fertilisation</h3>
    <p>Recommande le type d'engrais adapté selon l'analyse NPK
    du sol et la culture.</p>
    <p><b>Algorithme :</b> XGBoost<br>
    <b>Accuracy :</b> 95.42% | F1 : 95.47%<br>
    <b>Engrais :</b> DAP · Urée · NPK 15-15-15</p>
</div>""", unsafe_allow_html=True)

with col3:
    st.markdown("""
<div class="module-card">
    <h3 style="color:#e65100">🔬 Module Maladies</h3>
    <p>Détecte les maladies via photo de feuille (CNN) ou
    indices NDVI <b>avec météo temps réel</b>.</p>
    <p><b>Algorithme :</b> CNN MobileNetV2 + Transfer Learning<br>
    <b>Val accuracy :</b> 96.61%<br>
    <b>Données météo :</b> 🛰️ Open-Meteo (temps réel)</p>
</div>""", unsafe_allow_html=True)

st.divider()

# ── Contexte ──────────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("""
**🌾 Cultures couvertes :**
- Mil *(Pennisetum glaucum)*
- Sorgho *(Sorghum bicolor)*
- Arachide *(Arachis hypogaea)*
- Maïs *(Zea mays)*
- Coton *(Gossypium hirsutum)*
""")

with col_b:
    st.markdown("""
**🗺️ Zones géographiques :**
- Zone sahélienne : N'Djamena, Abéché
- Zone soudanienne : Sarh, Moundou, Bongor

**📡 Sources de données :**
- NASA POWER (entraînement — 2015–2023)
- Open-Meteo API (météo temps réel)
- PlantVillage + mais-disease (images)
""")

# ── API météo info ────────────────────────────────────────────────
st.info(
    "🛰️ **Météo temps réel intégrée** — Les modules Irrigation et "
    "Détection des Maladies utilisent l'API **Open-Meteo** (gratuite, sans clé) "
    "pour pré-remplir automatiquement les données climatiques des 5 villes tchadiennes."
)

st.info("👈 Utilisez le **menu de gauche** pour accéder aux 3 modules.")

st.divider()
st.caption(
    "PFE Licence 3 Informatique — ENASTIC 2025/2026 | "
    "Étudiant : TOURABI ISSAK HISSEIN | "
    "Encadreur : Dr. MOUAZ MIKAIL | "
    "Météo : Open-Meteo API (open-meteo.com)"
)
