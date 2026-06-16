# ══════════════════════════════════════════════════════════════════
# pages/3_🔬_Detection_Maladies.py
# Module Détection des Maladies — CNN MobileNetV2
# ══════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np
import json, os
from PIL import Image

st.set_page_config(
    page_title="Détection Maladies", page_icon="🔬", layout="wide")

# ── Chargement CNN ────────────────────────────────────────────────
@st.cache_resource
def charger_cnn():
    base = os.path.dirname(os.path.dirname(__file__))
    h5   = os.path.join(base, "models", "model_maladie_cnn.h5")
    cfg  = os.path.join(base, "models", "config_maladies.json")
    try:
        import tensorflow as tf
        model   = tf.keras.models.load_model(h5)
        config  = json.load(open(cfg)) if os.path.exists(cfg) else {}
        classes = config.get('classes', [])
        return model, classes, True
    except Exception as e:
        return None, [], False

model_cnn, CLASSES, cnn_ok = charger_cnn()

# ── Conseils traitement ───────────────────────────────────────────
CONSEILS = {
    "Mais_Malade":     "Appliquer un fongicide à base de mancozèbe (2–3 kg/ha). "
                       "Surveiller la progression sur 7 jours.",
    "Mais_Saine":      "Parcelle saine. Maintenir la surveillance hebdomadaire.",
    "Sorgho_Malade":   "Traitement fongicide foliaire recommandé. "
                       "Vérifier l'humidité — les maladies progressent avec l'excès d'eau.",
    "Sorgho_Saine":    "Parcelle saine. Suivi normal.",
    "Arachide_Malade": "Chlorothalonil 1.5 L/ha en 2 applications espacées de 14 jours.",
    "Arachide_Saine":  "Parcelle saine. Vérifier le sol.",
    "Mil_Malade":      "Métalaxyl-M + mancozèbe recommandés en saison des pluies.",
    "Mil_Saine":       "Parcelle saine. Continuer le suivi.",
    "Coton_Malade":    "Insecticide + fongicide combiné. Consulter un agronome ITRAD.",
    "Coton_Saine":     "Parcelle saine. Surveillance des parasites recommandée.",
}

# ── Interface ────────────────────────────────────────────────────
st.title("🔬 Module Détection des Maladies")
st.markdown(
    "Diagnostic foliaire par intelligence artificielle — "
    "**CNN MobileNetV2 + Transfer Learning** (val accuracy : 96.61%)"
)

if not cnn_ok:
    st.error(
        "⚠️ Modèle CNN non trouvé. Placez `model_maladie_cnn.h5` "
        "et `config_maladies.json` dans le dossier `models/`"
    )
    st.stop()

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Photo de la feuille")
    st.info(
        "Prenez une photo claire d'une feuille de la plante à analyser. "
        "La photo doit montrer la feuille entière sur fond neutre si possible."
    )
    photo = st.file_uploader(
        "Charger une photo (JPG, PNG)",
        type=["jpg", "jpeg", "png"],
        help="Photo prise avec un smartphone ou une caméra de drone"
    )
    culture_hint = st.selectbox(
        "Culture concernée (optionnel — aide à l'interprétation)",
        ["Non précisé", "Mais", "Sorgho", "Arachide", "Mil", "Coton"]
    )

    if photo:
        img = Image.open(photo)
        st.image(img, caption="Photo chargée", use_column_width=True)

with col2:
    st.subheader("📊 Diagnostic")

    if photo is None:
        st.markdown("""
        **Instructions :**
        1. Chargez une photo de feuille à gauche
        2. Sélectionnez la culture (optionnel)
        3. Cliquez sur **Analyser**

        **Cultures supportées :**
        - 🌽 Maïs
        - 🌾 Sorgho
        - 🥜 Arachide
        - 🌾 Mil
        - 🌿 Coton
        """)
    else:
        if st.button("🔍 Analyser la feuille", type="primary",
                     use_container_width=True):

            with st.spinner("Analyse en cours..."):
                # Prétraitement identique à l'entraînement
                img_resized = img.convert("RGB").resize((224, 224))
                img_array  = np.array(img_resized) / 255.0
                img_batch  = np.expand_dims(img_array, axis=0)

                # Prédiction
                predictions = model_cnn.predict(img_batch, verbose=0)[0]
                idx_pred    = int(np.argmax(predictions))
                confiance   = float(predictions[idx_pred]) * 100

                if CLASSES and idx_pred < len(CLASSES):
                    classe_predite = CLASSES[idx_pred]
                else:
                    classe_predite = f"Classe {idx_pred}"

                # Parsing du résultat
                parts   = classe_predite.split("_")
                culture = parts[0] if parts else "Inconnue"
                etat    = parts[1] if len(parts) > 1 else "Inconnu"

            # ── Affichage résultat ────────────────────────────────
            if "Malade" in classe_predite:
                st.error(f"🦠 **MALADIE DÉTECTÉE** sur {culture}")
                couleur = "#c0392b"
            else:
                st.success(f"✅ **{culture} SAIN(E)**")
                couleur = "#27ae60"

            st.metric("Confiance du modèle", f"{confiance:.1f}%")
            st.metric("Culture détectée", culture)
            st.metric("État", etat)

            # Conseil
            conseil = CONSEILS.get(classe_predite, "Consultez un agronome.")
            st.info(f"**Recommandation :** {conseil}")

            # Top 5 probabilités
            with st.expander("Détail des probabilités (toutes classes)"):
                indices_tries = np.argsort(predictions)[::-1][:5]
                for i in indices_tries:
                    cls = CLASSES[i] if CLASSES and i < len(CLASSES) else f"Classe {i}"
                    prb = predictions[i] * 100
                    st.progress(float(predictions[i]),
                                text=f"{cls} : {prb:.1f}%")

            st.caption(
                "Modèle : CNN MobileNetV2 + Transfer Learning | "
                "Données : PlantVillage + mais-disease | "
                "Val accuracy Phase 1 : 96.61%"
            )

# ── Avertissement ────────────────────────────────────────────────
st.divider()
st.warning(
    "⚠️ Ce système est un outil d'aide à la décision. "
    "En cas de doute, consultez un agronome ou l'ITRAD "
    "(Institut Tchadien de Recherche Agronomique pour le Développement)."
)
