# ══════════════════════════════════════════════════════════════════
# pages/1_💧_Irrigation.py
# Module Irrigation — Random Forest
# ══════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np
import joblib
import os

st.set_page_config(page_title="Irrigation", page_icon="💧", layout="wide")

# ── Chargement du modèle (mis en cache) ──────────────────────────
@st.cache_resource
def charger_modele_irrigation():
    """Charge le modèle et le scaler une seule fois au démarrage."""
    base = os.path.dirname(os.path.dirname(__file__))
    try:
        model  = joblib.load(os.path.join(base, "models", "model_irrigation.pkl"))
        scaler = joblib.load(os.path.join(base, "models", "scaler_irrigation.pkl"))
        return model, scaler, True
    except FileNotFoundError:
        return None, None, False

model_irr, scaler_irr, modele_ok = charger_modele_irrigation()

# ── En-tête ──────────────────────────────────────────────────────
st.title("💧 Module Irrigation")
st.markdown(
    "Prédiction du besoin en irrigation basée sur les données "
    "climatiques et agronomiques — **Random Forest** (Accuracy : 78.51%)"
)

if not modele_ok:
    st.error(
        "⚠️ Modèle non trouvé. Placez `model_irrigation.pkl` et "
        "`scaler_irrigation.pkl` dans le dossier `models/`"
    )
    st.stop()

st.divider()

# ── Formulaire de saisie ─────────────────────────────────────────
st.subheader("📥 Données de la parcelle")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🌡️ Données climatiques**")
    temperature_moy = st.slider("Température moyenne (°C)", 15.0, 45.0, 32.0, 0.5)
    temperature_max = st.slider("Température maximale (°C)", 20.0, 50.0,
                                 temperature_moy + 7.0, 0.5)
    pluie_7j  = st.number_input("Pluie cumulée 7 jours (mm)", 0.0, 200.0, 5.0, 1.0)
    pluie_14j = st.number_input("Pluie cumulée 14 jours (mm)", 0.0, 300.0,
                                  pluie_7j * 1.8, 1.0)
    humidite_air        = st.slider("Humidité de l'air (%)", 5.0, 95.0, 35.0, 1.0)
    vent_moy            = st.slider("Vitesse du vent (m/s)", 0.0, 15.0, 3.0, 0.5)
    rayonnement_solaire = st.slider("Rayonnement solaire (MJ/m²/j)",
                                     10.0, 30.0, 22.0, 0.5)

with col2:
    st.markdown("**🌱 Sol et culture**")
    humidite_sol = st.slider("Humidité du sol (%)", 5.0, 90.0, 20.0, 1.0)
    etp          = st.slider("Évapotranspiration (mm/j)", 2.0, 14.0, 7.0, 0.1)
    ph_sol       = st.slider("pH du sol", 5.0, 9.0, 7.0, 0.1)

    culture = st.selectbox(
        "Culture",
        ["Mil", "Sorgho", "Arachide", "Mais", "Coton"],
        index=0
    )
    culture_map = {"Arachide": 0, "Coton": 1, "Mais": 2, "Mil": 3, "Sorgho": 4}
    culture_enc = culture_map[culture]

    stade = st.selectbox(
        "Stade phénologique",
        ["Semis", "Levée", "Floraison", "Maturation", "Repos"],
        index=2,
        help="La floraison est le stade le plus sensible au stress hydrique"
    )
    stade_map = {"Floraison": 0, "Levée": 1, "Maturation": 2, "Repos": 3, "Semis": 4}
    stade_enc = stade_map[stade]

with col3:
    st.markdown("**🗺️ Zone géographique**")
    zone = st.selectbox("Zone", ["Sahélienne", "Soudanienne"], index=0)
    zone_enc = 0 if zone == "Sahélienne" else 1

    saison = st.selectbox(
        "Saison",
        ["Sèche", "Début des pluies", "Saison des pluies"],
        index=0
    )
    saison_map = {"Début des pluies": 0, "Saison des pluies": 1, "Sèche": 2}
    saison_enc = saison_map[saison]

    type_sol = st.selectbox(
        "Type de sol",
        ["Argileux", "Limoneux", "Sableux"],
        index=2,
        help="Les sols sableux drainent rapidement et nécessitent plus d'irrigation"
    )
    sol_map = {"Argileux": 0, "Limoneux": 1, "Sableux": 2}
    type_sol_enc = sol_map[type_sol]

    st.markdown("---")
    st.info(f"**Culture :** {culture} | **Zone :** {zone}")
    st.info(f"**Stade :** {stade} | **Saison :** {saison}")

# ── Prédiction ───────────────────────────────────────────────────
st.divider()

if st.button("🔍 Analyser le besoin en irrigation", type="primary",
             use_container_width=True):

    X_input = np.array([[
        temperature_moy, temperature_max,
        pluie_7j, pluie_14j,
        humidite_air, humidite_sol, etp,
        vent_moy, rayonnement_solaire,
        culture_enc, stade_enc, saison_enc,
        type_sol_enc, ph_sol, zone_enc
    ]])

    X_scaled = scaler_irr.transform(X_input)
    prediction = model_irr.predict(X_scaled)[0]
    proba      = model_irr.predict_proba(X_scaled)[0]
    confiance  = proba[prediction] * 100

    # ── Résultat ─────────────────────────────────────────────────
    st.subheader("📊 Résultat")
    col_res1, col_res2, col_res3 = st.columns(3)

    with col_res1:
        if prediction == 1:
            st.markdown(
                '<div class="result-danger">'
                '✅ IRRIGATION RECOMMANDÉE</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="result-ok">'
                '❌ IRRIGATION NON NÉCESSAIRE</div>',
                unsafe_allow_html=True)

    with col_res2:
        st.metric("Confiance du modèle", f"{confiance:.1f}%")

    with col_res3:
        if prediction == 1:
            dose = round(max(0, 40 - humidite_sol) * 0.5 + etp * 1.8, 1)
            st.metric("Dose recommandée", f"{dose} mm")

    # Détails
    if prediction == 1:
        st.warning(
            f"🌾 **{culture}** en phase **{stade}** nécessite une irrigation. "
            f"Créneau optimal : **matin tôt (5h–8h)** pour limiter l'évaporation."
        )
    else:
        st.success(
            f"La parcelle de **{culture}** dispose de suffisamment d'humidité. "
            "Prochaine vérification recommandée dans 3–5 jours."
        )

    # Probabilités
    with st.expander("Détail des probabilités"):
        col_p1, col_p2 = st.columns(2)
        col_p1.metric("Probabilité NON irriguer", f"{proba[0]*100:.1f}%")
        col_p2.metric("Probabilité OUI irriguer", f"{proba[1]*100:.1f}%")

        st.caption(
            f"Modèle : Random Forest | "
            f"Données : NASA POWER (5 villes Tchad 2015–2023) | "
            f"Accuracy : 78.51% | AUC-ROC : 0.878"
        )
