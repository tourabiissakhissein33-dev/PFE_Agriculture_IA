# ══════════════════════════════════════════════════════════════════
# pages/3_Detection_Maladies.py
# Module Détection des Maladies — CNN MobileNetV2 + Météo Open-Meteo
# ══════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np
import json, os, sys
from PIL import Image

st.set_page_config(
    page_title="Détection Maladies", page_icon="🔬", layout="wide")

# ── Import utilitaire météo ───────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from meteo_api import VILLES_TCHAD, get_meteo_actuelle, afficher_meteo_widget

# ── Chargement CNN robuste ────────────────────────────────────────
@st.cache_resource
def charger_cnn():
    chemins = [
        os.path.join(ROOT, "models"),
        os.path.join(os.getcwd(), "models"),
        "models",
    ]
    for base in chemins:
        h5  = os.path.join(base, "model_maladie_cnn.h5")
        cfg = os.path.join(base, "config_maladies.json")
        if not os.path.exists(h5):
            continue
        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(h5)
            classes = []
            if os.path.exists(cfg):
                with open(cfg) as f:
                    classes = json.load(f).get("classes", [])
            return model, classes, True
        except Exception as e:
            st.warning(f"Erreur chargement CNN : {e}")
            return None, [], False
    return None, [], False

model_cnn, CLASSES, CNN_OK = charger_cnn()

# ── Conseils agronomiques ─────────────────────────────────────────
CONSEILS = {
    "Mais_Malade":     ("🔴 MALADIE DÉTECTÉE",
                        "Appliquer fongicide mancozèbe 2–3 kg/ha. Surveiller 7 jours.",
                        "error"),
    "Mais_Saine":      ("🟢 MAÏS SAIN",
                        "Parcelle saine. Surveillance hebdomadaire recommandée.",
                        "success"),
    "Sorgho_Malade":   ("🔴 MALADIE DÉTECTÉE",
                        "Fongicide foliaire recommandé. Réduire l'humidité excessive.",
                        "error"),
    "Sorgho_Saine":    ("🟢 SORGHO SAIN",     "Parcelle saine. Suivi normal.",          "success"),
    "Arachide_Malade": ("🔴 MALADIE DÉTECTÉE",
                        "Chlorothalonil 1.5 L/ha — 2 applications à 14j d'intervalle.",
                        "error"),
    "Arachide_Saine":  ("🟢 ARACHIDE SAINE",  "Parcelle saine. Vérifier le sol.",        "success"),
    "Mil_Malade":      ("🔴 MALADIE DÉTECTÉE",
                        "Métalaxyl-M + mancozèbe recommandés.",
                        "error"),
    "Mil_Saine":       ("🟢 MIL SAIN",        "Parcelle saine. Continuer le suivi.",     "success"),
    "Coton_Malade":    ("🔴 MALADIE DÉTECTÉE",
                        "Insecticide + fongicide combiné. Consulter l'ITRAD.",
                        "error"),
    "Coton_Saine":     ("🟢 COTON SAIN",
                        "Parcelle saine. Surveiller les parasites.",
                        "success"),
}

# ── Diagnostic NDVI (règles agronomiques — toujours disponible) ───
def diagnostiquer_ndvi(ndvi, culture, temperature, humidite_air, pluie_7j):
    seuils = {
        "Mais":    {"critique": 0.25, "alerte": 0.40},
        "Sorgho":  {"critique": 0.22, "alerte": 0.38},
        "Arachide":{"critique": 0.28, "alerte": 0.42},
        "Mil":     {"critique": 0.20, "alerte": 0.35},
        "Coton":   {"critique": 0.30, "alerte": 0.45},
    }
    s     = seuils.get(culture, {"critique": 0.25, "alerte": 0.40})
    score = 0
    raisons = []

    if ndvi < s["critique"]:
        score += 4
        raisons.append(f"NDVI très faible ({ndvi:.2f} < {s['critique']})")
    elif ndvi < s["alerte"]:
        score += 2
        raisons.append(f"NDVI faible ({ndvi:.2f} < {s['alerte']})")

    if temperature > 35:
        score += 1
        raisons.append(f"Température élevée ({temperature}°C)")
    if humidite_air > 75 and ndvi < 0.4:
        score += 1
        raisons.append("Humidité élevée → risque fongique")
    if pluie_7j > 50 and ndvi < 0.4:
        score += 1
        raisons.append("Excès de pluie → risque maladie")

    if score >= 4:
        return "Malade", min(90, 60 + score * 5), raisons
    elif score >= 2:
        return "Stress", min(80, 50 + score * 5), raisons
    else:
        return "Saine", min(95, 75 + (5 - score) * 3), raisons

# ══════════════════════════════════════════════════════════════════
# INTERFACE
# ══════════════════════════════════════════════════════════════════

st.title("🔬 Module Détection des Maladies")

if CNN_OK:
    st.success(
        "✅ Modèle CNN MobileNetV2 chargé — "
        f"val accuracy : 96.61% | {len(CLASSES)} classes"
    )
else:
    st.info(
        "ℹ️ Modèle CNN non chargé. "
        "**Mode actif : Diagnostic NDVI + données météo temps réel**"
    )

st.divider()

# ══════════════════════════════════════════════════════════════════
# MÉTÉO TEMPS RÉEL
# ══════════════════════════════════════════════════════════════════

st.subheader("🛰️ Conditions météo de la parcelle (Open-Meteo)")

col_v1, col_v2 = st.columns([2, 1])
with col_v1:
    ville_sel = st.selectbox(
        "Ville la plus proche",
        list(VILLES_TCHAD.keys()),
        index=0
    )
with col_v2:
    btn_meteo = st.button("🔄 Charger la météo", use_container_width=True)

if "meteo_mal" not in st.session_state:
    st.session_state.meteo_mal = None
if "ville_mal" not in st.session_state:
    st.session_state.ville_mal = ville_sel

if btn_meteo or st.session_state.ville_mal != ville_sel:
    st.session_state.ville_mal = ville_sel
    coords = VILLES_TCHAD[ville_sel]
    with st.spinner(f"Chargement météo {ville_sel}..."):
        st.session_state.meteo_mal = get_meteo_actuelle(
            coords["lat"], coords["lon"])

meteo = st.session_state.meteo_mal
if meteo:
    afficher_meteo_widget(meteo, ville_sel)

st.divider()

# ══════════════════════════════════════════════════════════════════
# ONGLETS
# ══════════════════════════════════════════════════════════════════

if CNN_OK:
    tab1, tab2 = st.tabs([
        "📸 Analyse par photo (CNN MobileNetV2)",
        "📡 Analyse NDVI (Télédétection)"
    ])
else:
    tab2, = st.tabs(["📡 Analyse NDVI (Télédétection)"])
    tab1 = None

# ── TAB 1 : CNN ───────────────────────────────────────────────────
if tab1:
    with tab1:
        st.subheader("📸 Diagnostic par photo de feuille")
        col_a, col_b = st.columns([1, 1])

        with col_a:
            st.info("Prenez une photo claire d'une feuille — fond neutre de préférence.")
            photo = st.file_uploader(
                "Charger une photo (JPG, PNG)",
                type=["jpg","jpeg","png"],
                key="photo_cnn"
            )
            culture_hint = st.selectbox(
                "Culture (optionnel)",
                ["Non précisé","Mais","Sorgho","Arachide","Mil","Coton"],
                key="cult_hint"
            )
            if photo:
                img_orig = Image.open(photo)
                st.image(img_orig, caption="Photo originale", use_column_width=True)

        with col_b:
            if not photo:
                st.markdown("**👈 Chargez une photo pour commencer**")
                st.markdown("""
                **Cultures supportées :**
                🌽 Maïs · 🌾 Sorgho · 🥜 Arachide · 🌾 Mil · 🌿 Coton
                """)
            else:
                if st.button("🔍 Analyser la feuille", type="primary",
                             use_container_width=True, key="btn_cnn"):
                    with st.spinner("Analyse CNN en cours..."):
                        img_r = img_orig.convert("RGB").resize((224, 224))
                        arr   = np.expand_dims(np.array(img_r)/255.0, axis=0)
                        preds = model_cnn.predict(arr, verbose=0)[0]
                        idx   = int(np.argmax(preds))
                        conf  = float(preds[idx]) * 100
                        cls   = CLASSES[idx] if CLASSES and idx < len(CLASSES) else f"Classe {idx}"

                    titre, conseil, typ = CONSEILS.get(
                        cls, (cls, "Consultez un agronome.", "warning"))

                    getattr(st, typ)(f"**{titre}**")
                    st.metric("Confiance du modèle", f"{conf:.1f}%")

                    # Contexte météo
                    if meteo and meteo["ok"]:
                        st.info(
                            f"📍 Conditions à {ville_sel} : "
                            f"T°={meteo['temperature_moy']}°C · "
                            f"Humidité={meteo['humidite_air']}% · "
                            f"Pluie 7j={meteo['pluie_7j']}mm"
                        )

                    st.info(f"**Recommandation :** {conseil}")

                    with st.expander("Toutes les probabilités"):
                        for i in np.argsort(preds)[::-1][:5]:
                            c = CLASSES[i] if CLASSES and i < len(CLASSES) else f"Classe {i}"
                            st.progress(float(preds[i]),
                                        text=f"{c} : {preds[i]*100:.1f}%")

                    st.caption(
                        "CNN MobileNetV2 + Transfer Learning | "
                        "PlantVillage + mais-disease | val accuracy : 96.61%"
                    )

# ── TAB 2 : NDVI ─────────────────────────────────────────────────
with tab2:
    st.subheader("📡 Diagnostic par indices spectraux NDVI")
    st.markdown(
        "Entrez les valeurs NDVI de votre parcelle "
        "(obtenues par satellite Sentinel-2 ou drone multispectral). "
        "Les données météo sont **pré-remplies automatiquement** si vous avez chargé la météo."
    )

    # Valeurs par défaut depuis la météo temps réel
    t_def   = meteo["temperature_moy"]  if meteo and meteo["ok"] else 33.0
    hu_def  = meteo["humidite_air"]     if meteo and meteo["ok"] else 40.0
    pl_def  = meteo["pluie_7j"]         if meteo and meteo["ok"] else 10.0

    col_n1, col_n2, col_n3 = st.columns(3)

    with col_n1:
        st.markdown("**📊 Indices spectraux**")
        ndvi = st.slider("NDVI", -1.0, 1.0, 0.35, 0.01,
                         help="< 0.3 : stress | 0.3–0.5 : modéré | > 0.5 : sain")
        if ndvi > 0.5:
            st.success(f"🟢 NDVI = {ndvi:.2f} — Végétation saine")
        elif ndvi > 0.3:
            st.warning(f"🟡 NDVI = {ndvi:.2f} — Stress modéré")
        else:
            st.error(f"🔴 NDVI = {ndvi:.2f} — Stress sévère")
        evi  = st.slider("EVI",  -1.0, 1.0, 0.28, 0.01)
        savi = st.slider("SAVI", -1.0, 1.0, 0.32, 0.01)

    with col_n2:
        st.markdown("**🌡️ Conditions climatiques**")
        if meteo and meteo["ok"]:
            st.caption("✅ Pré-rempli depuis Open-Meteo")
        temperature = st.slider(
            "Température (°C)", 15.0, 45.0, float(t_def), 0.5)
        humidite_nd = st.slider(
            "Humidité de l'air (%)", 10.0, 95.0, float(hu_def), 1.0)
        pluie_ndvi  = st.number_input(
            "Pluie 7 derniers jours (mm)", 0.0, 300.0, float(pl_def), 1.0)

    with col_n3:
        st.markdown("**🌾 Parcelle**")
        culture_nd = st.selectbox(
            "Culture", ["Mais","Sorgho","Arachide","Mil","Coton"],
            index=0, key="cult_ndvi")
        saison_nd  = st.selectbox(
            "Saison",
            ["Sèche","Début des pluies","Saison des pluies"],
            index=2, key="sais_ndvi")
        zone_nd    = st.selectbox(
            "Zone",
            ["Sahélienne","Soudanienne"],
            index=0 if VILLES_TCHAD.get(ville_sel,{}).get("zone","Sahélienne")=="Sahélienne" else 1,
            key="zone_ndvi")

    st.divider()

    if st.button("🔍 Analyser la parcelle (NDVI)", type="primary",
                 use_container_width=True, key="btn_ndvi"):

        niveau, confiance, raisons = diagnostiquer_ndvi(
            ndvi, culture_nd, temperature, humidite_nd, pluie_ndvi)

        col_r1, col_r2, col_r3 = st.columns(3)

        cls_key = f"{culture_nd}_{niveau}" if niveau in ("Malade","Saine") else None
        if cls_key and cls_key in CONSEILS:
            titre, conseil, typ = CONSEILS[cls_key]
        elif niveau == "Stress":
            titre   = "🟡 STRESS VÉGÉTATIF"
            conseil = f"Surveillance renforcée pour {culture_nd}. Vérifier eau et nutriments."
            typ     = "warning"
        else:
            titre   = f"État : {niveau}"
            conseil = "Consultez un agronome."
            typ     = "info"

        with col_r1:
            getattr(st, typ)(f"**{titre}**")
        with col_r2:
            st.metric("Confiance", f"{confiance:.0f}%")
            st.metric("Culture",   culture_nd)
        with col_r3:
            st.metric("NDVI",      f"{ndvi:.3f}")
            st.metric("Zone",      zone_nd)

        st.info(f"**Recommandation :** {conseil}")

        if raisons:
            with st.expander("🔍 Facteurs identifiés"):
                for r in raisons:
                    st.markdown(f"- {r}")

        if meteo and meteo["ok"]:
            st.success(
                f"📍 Météo temps réel ({ville_sel}) intégrée dans l'analyse — "
                f"T°={temperature}°C · Humidité={humidite_nd}% · "
                f"Pluie 7j={pluie_ndvi}mm"
            )

        with st.expander("📊 Interprétation des indices"):
            c1, c2, c3 = st.columns(3)
            c1.metric("NDVI", f"{ndvi:.3f}",
                      "Sain" if ndvi > 0.5 else ("Modéré" if ndvi > 0.3 else "Critique"))
            c2.metric("EVI",  f"{evi:.3f}")
            c3.metric("SAVI", f"{savi:.3f}")
            st.markdown("""
| Indice | Valeur | Interprétation |
|--------|--------|----------------|
| NDVI > 0.5 | Dense | Plante saine |
| NDVI 0.3–0.5 | Modéré | Stress possible |
| NDVI < 0.3 | Faible | Maladie / stress sévère |
""")

st.divider()
st.warning(
    "⚠️ Outil d'aide à la décision. "
    "En cas de doute, consultez un agronome ou l'**ITRAD**."
)
