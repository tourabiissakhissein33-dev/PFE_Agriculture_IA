# ╔══════════════════════════════════════════════════════════════════╗
# ║  AGRO-IA — Application Streamlit                               ║
# ║  Cadre décisionnel IA pour l'agriculture tchadienne            ║
# ║  Étudiant : TOURABI ISSAK HISSEIN — ENASTIC 2025/2026          ║
# ╚══════════════════════════════════════════════════════════════════╝
# Fichier : app.py  (point d'entrée principal)

import streamlit as st

# ── Configuration de la page ──────────────────────────────────────
st.set_page_config(
    page_title="Agro-IA Tchad",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personnalisé ──────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a5276;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #5d6d7e;
        text-align: center;
        margin-bottom: 2rem;
    }
    .module-card {
        background: #f8f9fa;
        border-left: 4px solid #1a5276;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .result-ok {
        background: #e8f5e9;
        border-left: 4px solid #27ae60;
        border-radius: 8px;
        padding: 1rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .result-warn {
        background: #fff3e0;
        border-left: 4px solid #f39c12;
        border-radius: 8px;
        padding: 1rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .result-danger {
        background: #fce4e4;
        border-left: 4px solid #e74c3c;
        border-radius: 8px;
        padding: 1rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .metric-box {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 0.8rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Page d'accueil ────────────────────────────────────────────────
st.markdown('<div class="main-title">🌾 Agro-IA Tchad</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Cadre décisionnel basé sur l\'IA '
    'pour l\'optimisation du suivi parcellaire</div>',
    unsafe_allow_html=True)

st.divider()

# ── Présentation des 3 modules ────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="module-card">
        <h3 style="color:#1565c0">💧 Module Irrigation</h3>
        <p>Prédit le besoin en eau d'une parcelle à partir des données
        climatiques et du sol.</p>
        <p><b>Algorithme :</b> Random Forest<br>
        <b>Accuracy :</b> 78.51% | AUC-ROC : 0.878</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="module-card">
        <h3 style="color:#1b5e20">🌿 Module Fertilisation</h3>
        <p>Recommande le type d'engrais adapté selon l'analyse NPK
        du sol et la culture.</p>
        <p><b>Algorithme :</b> XGBoost<br>
        <b>Accuracy :</b> 95.42% | F1 : 95.47%</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="module-card">
        <h3 style="color:#e65100">🔬 Module Maladies</h3>
        <p>Détecte les maladies des cultures à partir d'une photo
        de feuille (CNN MobileNetV2).</p>
        <p><b>Algorithme :</b> CNN + Transfer Learning<br>
        <b>Val accuracy :</b> 96.61%</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Contexte du projet ────────────────────────────────────────────
st.subheader("📋 À propos du projet")
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("""
    **Cultures couvertes :**
    - 🌾 Mil (Pennisetum glaucum)
    - 🌾 Sorgho (Sorghum bicolor)
    - 🥜 Arachide (Arachis hypogaea)
    - 🌽 Maïs (Zea mays)
    - 🌿 Coton (Gossypium hirsutum)
    """)

with col_b:
    st.markdown("""
    **Zones géographiques :**
    - Zone sahélienne : N'Djamena, Abéché
    - Zone soudanienne : Sarh, Moundou, Bongor

    **Données utilisées :**
    - NASA POWER (données climatiques réelles)
    - PlantVillage (images maladies)
    """)

st.info(
    "👈 Utilisez le **menu de gauche** pour accéder aux 3 modules "
    "de recommandation agronomique."
)

# ── Footer ────────────────────────────────────────────────────────
st.divider()
st.caption(
    "PFE Licence 3 Informatique — ENASTIC 2025/2026 | "
    "Étudiant : TOURABI ISSAK HISSEIN | "
    "Encadreur : Dr. MOUAZ MIKAIL"
)
