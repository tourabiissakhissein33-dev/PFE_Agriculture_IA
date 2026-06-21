# ══════════════════════════════════════════════════════════════════
# pages/2_Fertilisation.py
# Module Fertilisation — XGBoost
# ══════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np
import joblib, os, sys

st.set_page_config(page_title="Fertilisation", page_icon="🌿", layout="wide")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@st.cache_resource
def charger_modele():
    chemins = [
        os.path.join(ROOT, "models"),
        os.path.join(os.getcwd(), "models"),
        "models",
    ]
    for base in chemins:
        try:
            model   = joblib.load(os.path.join(base, "model_fertilisation.pkl"))
            scaler  = joblib.load(os.path.join(base, "scaler_fertilisation.pkl"))
            le_eng  = joblib.load(os.path.join(base, "label_encoder_engrais.pkl"))
            le_cult = joblib.load(os.path.join(base, "label_encoder_culture.pkl"))
            le_sol  = joblib.load(os.path.join(base, "label_encoder_sol.pkl"))
            return model, scaler, le_eng, le_cult, le_sol, True
        except Exception:
            continue
    return None, None, None, None, None, False

model_f, scaler_f, le_eng, le_cult, le_sol, ok = charger_modele()

ENGRAIS_INFO = {
    "Uree": {
        "nom": "Urée (46-0-0)",
        "desc": "Engrais azoté — stimule la croissance végétative",
        "dose": "50–100 kg/ha",
        "moment": "Au semis et 30 jours après levée",
        "color": "#1565c0"
    },
    "DAP": {
        "nom": "DAP — Diammonium Phosphate (18-46-0)",
        "desc": "Apport phosphaté — favorise le développement racinaire",
        "dose": "50–75 kg/ha",
        "moment": "Au semis uniquement",
        "color": "#1b5e20"
    },
    "NPK_15_15_15": {
        "nom": "NPK 15-15-15 (engrais complet)",
        "desc": "Engrais équilibré — convient à toutes les cultures",
        "dose": "100–150 kg/ha",
        "moment": "Au semis",
        "color": "#4a148c"
    },
    "NPK_23_10_5": {
        "nom": "NPK 23-10-5 (riche en azote)",
        "desc": "Idéal pour maïs et céréales en phase végétative",
        "dose": "100–200 kg/ha",
        "moment": "Au semis + couverture à 30 jours",
        "color": "#bf360c"
    },
    "KCl": {
        "nom": "Chlorure de potassium — KCl (0-0-60)",
        "desc": "Apport potassique — améliore la résistance au stress",
        "dose": "30–50 kg/ha",
        "moment": "Au semis",
        "color": "#e65100"
    },
}

# ══════════════════════════════════════════════════════════════════
st.title("🌿 Module Fertilisation")
st.markdown(
    "Recommandation d'engrais basée sur l'analyse NPK du sol "
    "— **XGBoost** (Accuracy : 95.42%)"
)

if not ok:
    st.error("⚠️ Modèle non trouvé — placez les fichiers `.pkl` dans `models/`")
    st.stop()

st.divider()
st.subheader("📥 Analyse de la parcelle")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🧪 Analyse du sol (NPK)**")
    st.caption("Valeurs en kg/ha — issues d'une analyse de sol")
    N      = st.number_input("Azote — N (kg/ha)",      0.0, 200.0, 20.0, 1.0,
                              help="Valeur faible → Urée recommandée")
    P      = st.number_input("Phosphore — P (kg/ha)",  0.0, 100.0, 10.0, 1.0,
                              help="Valeur faible → DAP recommandé")
    K      = st.number_input("Potassium — K (kg/ha)",  0.0, 100.0, 15.0, 1.0,
                              help="Valeur faible → KCl recommandé")
    ph_sol = st.slider("pH du sol", 5.0, 9.0, 6.8, 0.1)

with col2:
    st.markdown("**🌡️ Conditions climatiques**")
    temperature  = st.slider("Température (°C)",     15.0, 45.0, 30.0, 0.5)
    humidite_air = st.slider("Humidité de l'air (%)",10.0, 95.0, 55.0, 1.0)
    humidite_sol = st.slider("Humidité du sol (%)",   5.0, 90.0, 40.0, 1.0)
    pluie        = st.number_input("Pluie récente (mm)", 0.0, 300.0, 50.0, 5.0)

with col3:
    st.markdown("**🌾 Culture et sol**")
    culture  = st.selectbox("Culture à fertiliser",
                             ["Mil","Sorgho","Arachide","Mais","Coton"], index=0)
    type_sol = st.selectbox("Type de sol",
                             ["Argileux","Limoneux","Sableux"], index=1)
    zone     = st.selectbox("Zone", ["Sahélienne","Soudanienne"], index=0)
    st.divider()
    st.info(f"**{culture}** — Sol {type_sol}\nN={N:.0f} | P={P:.0f} | K={K:.0f} kg/ha")

# Encodage
culture_enc  = le_cult.transform([culture])[0]  if le_cult  else 0
type_sol_enc = le_sol.transform([type_sol])[0]   if le_sol   else 0
zone_enc     = 0 if zone == "Sahélienne" else 1

st.divider()

if st.button("🔍 Recommander un engrais", type="primary",
             use_container_width=True):

    X_input = np.array([[
        N, K, P, temperature, humidite_air,
        humidite_sol, ph_sol, pluie,
        culture_enc, type_sol_enc, zone_enc
    ]])
    X_sc    = scaler_f.transform(X_input)
    pred    = model_f.predict(X_sc)[0]
    proba   = model_f.predict_proba(X_sc)[0]
    engrais = le_eng.inverse_transform([pred])[0]
    conf    = proba[pred] * 100
    info    = ENGRAIS_INFO.get(engrais, {})

    st.subheader("📊 Résultat")
    col_r1, col_r2 = st.columns([2, 1])

    with col_r1:
        couleur = info.get("color", "#1a5276")
        st.markdown(
            f'<div style="background:#f0f4f8;border-left:5px solid {couleur};'
            f'border-radius:8px;padding:1rem;margin-bottom:1rem">'
            f'<h3 style="color:{couleur};margin:0">🌿 {engrais}</h3>'
            f'<p style="margin:0.3rem 0 0">{info.get("nom","")}</p>'
            f'</div>', unsafe_allow_html=True)
        st.markdown(f"**Usage :** {info.get('desc','')}")
        st.markdown(f"**Dose recommandée :** {info.get('dose','')}")
        st.markdown(f"**Moment d'application :** {info.get('moment','')}")

    with col_r2:
        st.metric("Confiance", f"{conf:.1f}%")
        st.metric("Culture",   culture)
        st.metric("Sol",       type_sol)

    with st.expander("Distribution des probabilités"):
        for cls, p in zip(le_eng.classes_, proba):
            st.progress(float(p), text=f"{cls} : {p*100:.1f}%")

    st.caption(
        f"Modèle : XGBoost | Accuracy : 95.42% | "
        f"F1-macro : 95.47% | CV : 97.23% ± 1.11%"
    )
