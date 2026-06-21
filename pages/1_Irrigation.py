# ══════════════════════════════════════════════════════════════════
# pages/1_Irrigation.py  (sans emoji dans le nom du fichier)
# Module Irrigation — Random Forest + Météo Open-Meteo temps réel
# ══════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np
import joblib, os, sys

st.set_page_config(page_title="Irrigation", page_icon="💧", layout="wide")

# ── Import utilitaire météo ───────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from meteo_api import VILLES_TCHAD, get_meteo_actuelle, afficher_meteo_widget

# ── Chargement modèle ─────────────────────────────────────────────
@st.cache_resource
def charger_modele():
    chemins = [
        os.path.join(ROOT, "models"),
        os.path.join(os.getcwd(), "models"),
        "models",
    ]
    for base in chemins:
        m = os.path.join(base, "model_irrigation.pkl")
        s = os.path.join(base, "scaler_irrigation.pkl")
        if os.path.exists(m) and os.path.exists(s):
            return joblib.load(m), joblib.load(s), True
    return None, None, False

model_irr, scaler_irr, modele_ok = charger_modele()

# ══════════════════════════════════════════════════════════════════
# INTERFACE
# ══════════════════════════════════════════════════════════════════

st.title("💧 Module Irrigation")
st.markdown(
    "Prédiction du besoin en irrigation — **Random Forest** "
    "(Accuracy : 78.51% | AUC-ROC : 0.878)"
)

if not modele_ok:
    st.error("⚠️ Modèle non trouvé — placez `model_irrigation.pkl` et `scaler_irrigation.pkl` dans `models/`")
    st.stop()

st.divider()

# ══════════════════════════════════════════════════════════════════
# SECTION MÉTÉO TEMPS RÉEL
# ══════════════════════════════════════════════════════════════════

st.subheader("🛰️ Météo en temps réel (Open-Meteo)")

col_v1, col_v2 = st.columns([2, 1])
with col_v1:
    ville_sel = st.selectbox(
        "Ville / Zone",
        list(VILLES_TCHAD.keys()),
        index=0,
        help="Sélectionnez la ville la plus proche de votre parcelle"
    )
with col_v2:
    charger_meteo = st.button("🔄 Charger la météo", use_container_width=True)

# Initialiser la météo dans session_state
if "meteo_irr" not in st.session_state:
    st.session_state.meteo_irr = None
if "ville_irr" not in st.session_state:
    st.session_state.ville_irr = ville_sel

# Charger automatiquement si la ville change ou si bouton cliqué
if charger_meteo or st.session_state.ville_irr != ville_sel:
    st.session_state.ville_irr = ville_sel
    coords = VILLES_TCHAD[ville_sel]
    with st.spinner(f"Chargement météo {ville_sel}..."):
        st.session_state.meteo_irr = get_meteo_actuelle(
            coords["lat"], coords["lon"])

meteo = st.session_state.meteo_irr

# Afficher le widget météo
if meteo:
    afficher_meteo_widget(meteo, ville_sel)

st.divider()

# ══════════════════════════════════════════════════════════════════
# FORMULAIRE — pré-rempli avec la météo si disponible
# ══════════════════════════════════════════════════════════════════

# Valeurs par défaut : météo temps réel OU typiques du Tchad
t_moy_def    = meteo["temperature_moy"]   if meteo and meteo["ok"] else 34.0
t_max_def    = meteo["temperature_max"]   if meteo and meteo["ok"] else 41.0
hum_air_def  = meteo["humidite_air"]      if meteo and meteo["ok"] else 30.0
pluie_7_def  = meteo["pluie_7j"]          if meteo and meteo["ok"] else 5.0
pluie_14_def = meteo["pluie_14j"]         if meteo and meteo["ok"] else 9.0
vent_def     = meteo["vent_moy"]           if meteo and meteo["ok"] else 3.0
rad_def      = meteo["rayonnement"]        if meteo and meteo["ok"] else 22.0
etp_def      = meteo["etp"]               if meteo and meteo["ok"] else 7.0
sol_def      = meteo["humidite_sol"]       if meteo and meteo["ok"] else 20.0

# Badge source des données
if meteo and meteo["ok"]:
    st.info("✅ Formulaire pré-rempli avec la météo temps réel · Ajustez si nécessaire")
else:
    st.info("ℹ️ Valeurs typiques du Tchad · Chargez la météo pour des données en temps réel")

st.subheader("📥 Données de la parcelle")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🌡️ Données climatiques**")
    temperature_moy = st.slider(
        "Température moyenne (°C)", 15.0, 45.0,
        float(t_moy_def), 0.5)
    temperature_max = st.slider(
        "Température maximale (°C)", 20.0, 52.0,
        float(min(t_max_def, 52.0)), 0.5)
    pluie_7j = st.number_input(
        "Pluie cumulée 7 jours (mm)", 0.0, 250.0,
        float(pluie_7_def), 1.0)
    pluie_14j = st.number_input(
        "Pluie cumulée 14 jours (mm)", 0.0, 400.0,
        float(pluie_14_def), 1.0)
    humidite_air = st.slider(
        "Humidité de l'air (%)", 5.0, 95.0,
        float(hum_air_def), 1.0)
    vent_moy = st.slider(
        "Vitesse du vent (m/s)", 0.0, 15.0,
        float(min(vent_def, 15.0)), 0.5)
    rayonnement_solaire = st.slider(
        "Rayonnement solaire (MJ/m²/j)", 5.0, 35.0,
        float(min(rad_def, 35.0)), 0.5)

with col2:
    st.markdown("**🌱 Sol et culture**")
    humidite_sol = st.slider(
        "Humidité du sol (%)", 5.0, 90.0,
        float(min(sol_def, 90.0)), 1.0)
    etp = st.slider(
        "Évapotranspiration — ETP (mm/j)", 2.0, 14.0,
        float(min(etp_def, 14.0)), 0.1)
    ph_sol = st.slider("pH du sol", 5.0, 9.0, 7.0, 0.1)

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

    # Zone automatique selon la ville choisie
    zone_auto = VILLES_TCHAD.get(ville_sel, {}).get("zone", "Sahélienne")
    zone = st.selectbox(
        "Zone",
        ["Sahélienne", "Soudanienne"],
        index=0 if zone_auto == "Sahélienne" else 1
    )
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
        help="Les sols sableux drainent rapidement"
    )
    sol_map = {"Argileux": 0, "Limoneux": 1, "Sableux": 2}
    type_sol_enc = sol_map[type_sol]

    st.divider()
    st.info(f"**Culture :** {culture} | **Zone :** {zone}")
    st.info(f"**Stade :** {stade} | **Saison :** {saison}")

# ══════════════════════════════════════════════════════════════════
# PRÉDICTION
# ══════════════════════════════════════════════════════════════════

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

    X_scaled   = scaler_irr.transform(X_input)
    prediction = model_irr.predict(X_scaled)[0]
    proba      = model_irr.predict_proba(X_scaled)[0]
    confiance  = proba[prediction] * 100

    st.subheader("📊 Résultat")
    col_r1, col_r2, col_r3 = st.columns(3)

    with col_r1:
        if prediction == 1:
            st.error("✅ IRRIGATION RECOMMANDÉE")
        else:
            st.success("❌ IRRIGATION NON NÉCESSAIRE")

    with col_r2:
        st.metric("Confiance du modèle", f"{confiance:.1f}%")

    with col_r3:
        if prediction == 1:
            dose = round(max(0, 40 - humidite_sol) * 0.5 + etp * 1.8, 1)
            st.metric("Dose recommandée", f"{dose} mm")

    # Message contextuel
    if prediction == 1:
        st.warning(
            f"🌾 **{culture}** en phase **{stade}** à **{ville_sel}** "
            f"nécessite une irrigation. "
            f"Créneau optimal : **matin tôt (5h–8h)** pour limiter l'évaporation."
        )
    else:
        st.success(
            f"La parcelle de **{culture}** à **{ville_sel}** "
            f"dispose de suffisamment d'humidité. "
            "Prochaine vérification dans 3–5 jours."
        )

    # Détail probabilités
    with st.expander("Détail des probabilités"):
        col_p1, col_p2 = st.columns(2)
        col_p1.metric("Probabilité NON irriguer", f"{proba[0]*100:.1f}%")
        col_p2.metric("Probabilité OUI irriguer", f"{proba[1]*100:.1f}%")
        source = "Open-Meteo (temps réel)" if meteo and meteo["ok"] else "Saisie manuelle"
        st.caption(
            f"Modèle : Random Forest | Données : {source} | "
            f"Accuracy : 78.51% | AUC-ROC : 0.878"
        )
