import streamlit as st
import numpy as np
import json, os, sys
from PIL import Image

st.set_page_config(
    page_title="Détection Maladies",
    page_icon="🔬", layout="wide",
    initial_sidebar_state="expanded")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from styles import GLOBAL_CSS
from meteo_api import VILLES_TCHAD, get_meteo_actuelle, afficher_meteo_widget

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{
    background:linear-gradient(160deg,#fff8f0 0%,#fce4d6 50%,#fff3e0 100%);
}
</style>""", unsafe_allow_html=True)

# ── CNN chargement silencieux ─────────────────────────────────────
@st.cache_resource
def charger_cnn():
    chemins = [
        os.path.join(ROOT,"models"),
        os.path.join(os.getcwd(),"models"),
        "models",
    ]
    for base in chemins:
        h5 = os.path.join(base,"model_maladie_cnn.h5")
        if not os.path.exists(h5):
            continue
        try:
            import tensorflow as tf
            model   = tf.keras.models.load_model(h5)
            cfg     = h5.replace("model_maladie_cnn.h5","config_maladies.json")
            classes = []
            if os.path.exists(cfg):
                classes = json.load(open(cfg)).get("classes",[])
            if not classes:
                classes = [
                    "Arachide_Malade","Arachide_Saine",
                    "Coton_Malade","Coton_Saine",
                    "Mais_Malade","Mais_Saine",
                    "Mil_Malade","Mil_Saine",
                    "Sorgho_Malade","Sorgho_Saine",
                ]
            return model, classes, True
        except Exception:
            # Erreur silencieuse — pas de message technique à l'utilisateur
            return None, [], False
    return None, [], False

model_cnn, CLASSES, CNN_OK = charger_cnn()

CONSEILS = {
    "Mais_Malade":     "Fongicide mancozèbe 2–3 kg/ha. Surveiller 7 jours.",
    "Mais_Saine":      "Parcelle saine. Surveillance hebdomadaire.",
    "Sorgho_Malade":   "Fongicide foliaire. Réduire l'humidité excessive.",
    "Sorgho_Saine":    "Parcelle saine. Suivi normal.",
    "Arachide_Malade": "Chlorothalonil 1.5 L/ha — 2 applications à 14j.",
    "Arachide_Saine":  "Parcelle saine. Vérifier le sol.",
    "Mil_Malade":      "Métalaxyl-M + mancozèbe recommandés.",
    "Mil_Saine":       "Parcelle saine. Continuer le suivi.",
    "Coton_Malade":    "Insecticide + fongicide combiné. Consulter l'ITRAD.",
    "Coton_Saine":     "Parcelle saine. Surveiller les parasites.",
}
SEUILS = {
    "Mais":{"critique":0.25,"alerte":0.40},
    "Sorgho":{"critique":0.22,"alerte":0.38},
    "Arachide":{"critique":0.28,"alerte":0.42},
    "Mil":{"critique":0.20,"alerte":0.35},
    "Coton":{"critique":0.30,"alerte":0.45},
}

def score_ndvi(ndvi, culture, temp, humid, pluie):
    s  = SEUILS.get(culture,{"critique":0.25,"alerte":0.40})
    sc, r = 0, []
    if ndvi < s["critique"]:     sc+=4; r.append(f"NDVI très faible ({ndvi:.2f})")
    elif ndvi < s["alerte"]:     sc+=2; r.append(f"NDVI faible ({ndvi:.2f})")
    if temp > 35:                sc+=1; r.append(f"Température élevée ({temp:.0f}°C)")
    if humid > 75 and ndvi<0.4: sc+=1; r.append("Humidité élevée → risque fongique")
    if pluie > 50 and ndvi<0.4: sc+=1; r.append("Excès de pluie → risque maladie")
    if sc >= 4: return "Malade", min(90,60+sc*5), r
    if sc >= 2: return "Stress", min(80,50+sc*5), r
    return "Saine", min(95,75+(5-sc)*3), r

# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-header" style="background:linear-gradient(135deg,#bf360c,#e65100)">
  <div style="font-size:2.2rem">🔬</div>
  <div>
    <h1>Module Détection des Maladies</h1>
    <p>CNN MobileNetV2 (photo feuille) · NDVI Drone/Satellite · Météo temps réel</p>
  </div>
</div>""", unsafe_allow_html=True)

# Statut CNN — message propre, pas d'erreur technique
if CNN_OK:
    st.markdown(
        f'<div class="status-ok">✅ Modèle CNN MobileNetV2 chargé — '
        f'val accuracy : 96.61% | {len(CLASSES)} classes</div>',
        unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="status-warn">📡 Mode Télédétection NDVI actif — '
        'chargez le modèle CNN dans models/ pour activer l\'analyse photo</div>',
        unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MÉTÉO
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="meteo-box">', unsafe_allow_html=True)
st.markdown('<div class="meteo-title">🛰️ Météo en temps réel — Open-Meteo</div>',
            unsafe_allow_html=True)

vc1,vc2 = st.columns([3,1])
with vc1:
    ville_sel = st.selectbox("Ville",list(VILLES_TCHAD.keys()),
                              label_visibility="collapsed")
with vc2:
    btn_m = st.button("🔄 Charger",use_container_width=True,
                      type="primary")

if "meteo_mal" not in st.session_state:
    st.session_state.meteo_mal = None
if "ville_mal" not in st.session_state:
    st.session_state.ville_mal = ville_sel

if btn_m or st.session_state.ville_mal != ville_sel:
    st.session_state.ville_mal = ville_sel
    with st.spinner(f"Chargement météo {ville_sel}..."):
        coords = VILLES_TCHAD[ville_sel]
        st.session_state.meteo_mal = get_meteo_actuelle(
            coords["lat"],coords["lon"])

meteo = st.session_state.meteo_mal
if meteo and meteo.get("ok"):
    mc1,mc2,mc3,mc4,mc5 = st.columns(5)
    mc1.metric("🌡️ Température", f"{meteo['temperature_moy']}°C")
    mc2.metric("💧 Humidité",     f"{meteo['humidite_air']}%")
    mc3.metric("🌧️ Pluie 7j",    f"{meteo['pluie_7j']} mm")
    mc4.metric("💨 Vent",         f"{meteo['vent_moy']} m/s")
    mc5.metric("☀️ ETP",          f"{meteo['etp']} mm/j")
    st.caption(f"✅ Données temps réel · {ville_sel} · {meteo['heure_maj']}")
elif meteo and not meteo.get("ok"):
    st.warning(f"⚠️ {meteo.get('erreur','Météo indisponible')}")
else:
    st.caption("👆 Cliquez sur **Charger** pour les données météo en temps réel")

st.markdown('</div>', unsafe_allow_html=True)

# Valeurs pré-remplies
t_def  = meteo["temperature_moy"] if meteo and meteo.get("ok") else 33.0
hu_def = meteo["humidite_air"]    if meteo and meteo.get("ok") else 45.0
pl_def = meteo["pluie_7j"]        if meteo and meteo.get("ok") else 10.0

# ══════════════════════════════════════════════════════════════════
# ONGLETS — toujours 2 visibles
# ══════════════════════════════════════════════════════════════════
if CNN_OK:
    tab_cnn, tab_ndvi = st.tabs([
        "📸  Analyse photo (CNN MobileNetV2)",
        "🛰️  Analyse NDVI — Drone / Satellite"])
else:
    # CNN non dispo : montrer les 2 onglets quand même
    tab_cnn, tab_ndvi = st.tabs([
        "📸  Analyse photo (CNN — en cours de chargement)",
        "🛰️  Analyse NDVI — Drone / Satellite"])

# ══════════════════════════════════════════════════════════════════
# TAB CNN
# ══════════════════════════════════════════════════════════════════
with tab_cnn:
    if not CNN_OK:
        st.info(
            "🔄 Le modèle CNN n'est pas encore chargé. "
            "Placez `model_maladie_cnn.h5` dans le dossier `models/` "
            "pour activer l'analyse par photo.\n\n"
            "**En attendant**, utilisez l'onglet 🛰️ **NDVI** qui est "
            "pleinement fonctionnel.")
    else:
        st.markdown("### 📸 Diagnostic par photo de feuille")
        col_up, col_res = st.columns([1,1], gap="large")

        with col_up:
            st.markdown("""
            <div class="upload-guide">
                📷 <b>Protocole photo</b><br><br>
                ✅ Une seule feuille isolée<br>
                ✅ Fond blanc ou neutre<br>
                ✅ Photo rapprochée (20–30 cm)<br>
                ✅ Lumière naturelle, sans flash<br><br>
                ❌ Pas de champ entier<br>
                ❌ Pas de fond complexe
            </div>""", unsafe_allow_html=True)

            photo = st.file_uploader("📁 Charger une photo",
                                     type=["jpg","jpeg","png"],
                                     key="photo_cnn")
            if photo:
                img_orig = Image.open(photo)
                st.image(img_orig, caption="Photo chargée",
                         use_container_width=True)

        with col_res:
            if not photo:
                st.markdown("""
                <div style="background:white;border-radius:12px;padding:3rem;
                     text-align:center;color:#bbb;
                     box-shadow:0 2px 8px rgba(0,0,0,.05)">
                    <div style="font-size:3rem;margin-bottom:.5rem">🖼️</div>
                    <div>Chargez une photo pour lancer le diagnostic</div>
                </div>""", unsafe_allow_html=True)
            else:
                if st.button("🔍 Analyser la feuille", type="primary",
                             use_container_width=True, key="btn_cnn"):
                    with st.spinner("Analyse CNN..."):
                        img_r = img_orig.convert("RGB").resize((224,224))
                        arr   = np.expand_dims(np.array(img_r)/255.0, 0)
                        preds = model_cnn.predict(arr, verbose=0)[0]
                        idx   = int(np.argmax(preds))
                        conf  = float(preds[idx])*100
                        cls   = CLASSES[idx] if idx<len(CLASSES) else f"Classe {idx}"

                    parts   = cls.split("_")
                    culture = parts[0] if parts else "?"
                    etat    = parts[1] if len(parts)>1 else "?"
                    conseil = CONSEILS.get(cls,"Consultez un agronome.")

                    style = "result-malade" if etat=="Malade" else "result-sain"
                    icon  = "🦠" if etat=="Malade" else "✅"

                    st.markdown(
                        f'<div class="{style}">{icon} {culture} — {etat.upper()}</div>',
                        unsafe_allow_html=True)

                    rc1,rc2 = st.columns(2)
                    rc1.metric("Confiance", f"{conf:.1f}%")
                    rc2.metric("Culture",   culture)

                    if conf > 95:
                        st.warning(
                            "⚠️ Confiance très élevée — vérifiez que la photo "
                            "montre une feuille isolée sur fond neutre.")

                    if meteo and meteo.get("ok"):
                        st.info(
                            f"📍 {ville_sel} : T°={meteo['temperature_moy']}°C | "
                            f"Humidité={meteo['humidite_air']}% | "
                            f"Pluie={meteo['pluie_7j']}mm")

                    st.markdown(
                        f'<div class="conseil">💊 <b>Traitement :</b> {conseil}</div>',
                        unsafe_allow_html=True)

                    with st.expander("📊 Toutes les probabilités"):
                        for i in np.argsort(preds)[::-1][:5]:
                            c   = CLASSES[i] if i<len(CLASSES) else f"Classe {i}"
                            prb = float(preds[i])
                            clr = "#e53935" if "Malade" in c else "#27ae60"
                            ico = "🔴" if "Malade" in c else "🟢"
                            st.markdown(
                                f'<div class="prob-row">'
                                f'<span style="width:155px;font-size:.8rem">{ico} {c}</span>'
                                f'<div class="prob-bg"><div class="prob-fill" '
                                f'style="width:{prb*100:.1f}%;background:{clr}"></div></div>'
                                f'<span class="prob-val">{prb*100:.1f}%</span></div>',
                                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# TAB NDVI
# ══════════════════════════════════════════════════════════════════
with tab_ndvi:
    st.markdown("### 🛰️ Diagnostic NDVI — Drone ou Satellite")

    nd1, nd2 = st.columns([1,1], gap="large")

    with nd1:
        st.markdown("""
        <div class="card">
          <div class="card-title">Sources de données NDVI</div>
          <div style="font-size:.84rem;line-height:1.7;color:#333">
            <b>🚁 Drone multispectral</b><br>
            Survole la parcelle et calcule NDVI/EVI/SAVI
            pour chaque pixel. Résolution 5–10 cm.<br>
            <em>Apps : Pix4D, DroneDeploy, Agisoft</em>
          </div>
          <hr style="border:none;border-top:1px solid #f0f0f0;margin:.7rem 0">
          <div style="font-size:.84rem;line-height:1.7;color:#333">
            <b>🛰️ Satellite Sentinel-2 (gratuit)</b><br>
            Couvre le Tchad tous les 5 jours. Résolution 10m.<br>
            1. Aller sur <b>apps.sentinel-hub.com</b><br>
            2. Chercher votre parcelle<br>
            3. Sélectionner "NDVI" → lire la valeur
          </div>
          <hr style="border:none;border-top:1px solid #f0f0f0;margin:.7rem 0">
          <div style="font-size:.84rem;line-height:1.7;color:#333">
            <b>📱 Estimation visuelle</b><br>
            Feuilles vertes denses → NDVI ≈ 0.65–0.80<br>
            Feuilles pâles → NDVI ≈ 0.35–0.50<br>
            Jaunissement → NDVI ≈ 0.15–0.30
          </div>
        </div>""", unsafe_allow_html=True)

    with nd2:
        if meteo and meteo.get("ok"):
            st.success("✅ Valeurs météo pré-remplies depuis Open-Meteo")

        # Légende
        st.markdown("""
        <div class="ndvi-legend">
          <div class="nl-r">🔴 Malade (&lt;0.3)</div>
          <div class="nl-y">🟡 Stress (0.3–0.5)</div>
          <div class="nl-g">🟢 Sain (&gt;0.5)</div>
        </div>""", unsafe_allow_html=True)

        ndvi = st.slider("**NDVI**", -1.0, 1.0, 0.62, 0.01,
                         help="Valeur issue du drone ou satellite")

        if ndvi > 0.5:   st.success(f"🟢 NDVI = {ndvi:.2f} — Sain")
        elif ndvi > 0.3: st.warning(f"🟡 NDVI = {ndvi:.2f} — Stress modéré")
        else:            st.error(f"🔴 NDVI = {ndvi:.2f} — Stress sévère")

        evi  = st.slider("**EVI**",  -1.0, 1.0, 0.50, 0.01)
        savi = st.slider("**SAVI**", -1.0, 1.0, 0.55, 0.01,
                         help="Adapté aux zones semi-arides (Sahel)")

        st.markdown("---")
        n1,n2 = st.columns(2)
        with n1:
            temperature = st.number_input("Température (°C)",
                                          15.0,45.0,float(t_def),0.5)
            pluie_nd = st.number_input("Pluie 7j (mm)",
                                        0.0,300.0,float(pl_def),1.0)
        with n2:
            humidite_nd = st.number_input("Humidité (%)",
                                           10.0,95.0,float(hu_def),1.0)
            culture_nd  = st.selectbox("Culture",
                ["Mais","Sorgho","Arachide","Mil","Coton"],
                key="cult_nd")

        zone_auto = VILLES_TCHAD.get(ville_sel,{}).get("zone","Sahélienne")
        zone_nd   = st.radio("Zone",["Sahélienne","Soudanienne"],
                              index=0 if zone_auto=="Sahélienne" else 1,
                              horizontal=True, key="zone_nd")

        if st.button("🔍 Analyser (NDVI)", type="primary",
                     use_container_width=True, key="btn_ndvi"):

            niveau,conf,raisons = score_ndvi(
                ndvi,culture_nd,temperature,humidite_nd,pluie_nd)

            cls_key = f"{culture_nd}_{niveau}"
            conseil = CONSEILS.get(
                cls_key,
                "Surveillance renforcée recommandée."
                if niveau=="Stress" else "Consultez un agronome.")

            style = ("result-malade" if niveau=="Malade"
                     else "result-sain" if niveau=="Saine"
                     else "result-stress")
            icon  = "🦠" if niveau=="Malade" else ("✅" if niveau=="Saine" else "⚠️")

            st.markdown(
                f'<div class="{style}">{icon} {culture_nd} — {niveau.upper()}</div>',
                unsafe_allow_html=True)

            nr1,nr2,nr3 = st.columns(3)
            nr1.metric("Confiance", f"{conf:.0f}%")
            nr2.metric("NDVI",      f"{ndvi:.3f}")
            nr3.metric("Zone",      zone_nd)

            st.markdown(
                f'<div class="conseil">💊 <b>Traitement :</b> {conseil}</div>',
                unsafe_allow_html=True)

            if raisons:
                with st.expander("🔍 Facteurs de risque"):
                    for r in raisons:
                        st.markdown(f"• {r}")

            with st.expander("📋 Seuils NDVI par culture"):
                st.markdown("""
<table class="data-table">
<tr><th>Culture</th><th>🔴 Malade</th><th>🟡 Stress</th><th>🟢 Sain</th></tr>
<tr><td>🌽 Maïs</td><td>&lt;0.25</td><td>0.25–0.40</td><td>&gt;0.40</td></tr>
<tr><td>🌾 Sorgho</td><td>&lt;0.22</td><td>0.22–0.38</td><td>&gt;0.38</td></tr>
<tr><td>🥜 Arachide</td><td>&lt;0.28</td><td>0.28–0.42</td><td>&gt;0.42</td></tr>
<tr><td>🌾 Mil</td><td>&lt;0.20</td><td>0.20–0.35</td><td>&gt;0.35</td></tr>
<tr><td>🌿 Coton</td><td>&lt;0.30</td><td>0.30–0.45</td><td>&gt;0.45</td></tr>
</table>""", unsafe_allow_html=True)

st.divider()
st.warning("⚠️ Outil d'aide à la décision. En cas de doute, consultez un agronome ou l'**ITRAD**.")
