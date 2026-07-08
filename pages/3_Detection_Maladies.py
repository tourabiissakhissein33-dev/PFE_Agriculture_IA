import streamlit as st
import numpy as np
import json, os, sys
from PIL import Image

st.set_page_config(page_title="Détection Maladies",page_icon="🔬",
                   layout="wide",initial_sidebar_state="expanded")
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path: sys.path.insert(0,ROOT)
from styles import GLOBAL_CSS
from meteo_api import VILLES_TCHAD, get_meteo_actuelle
from database import sauvegarder_maladie

st.markdown(GLOBAL_CSS,unsafe_allow_html=True)
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:linear-gradient(160deg,#fff8f0 0%,#fce4d6 50%,#fff3e0 100%)}
.drone-card{border-radius:12px;padding:1rem 1.3rem;margin-bottom:.8rem;font-size:.84rem;line-height:1.7}
.ndvi-result{font-size:2rem;font-weight:900;text-align:center;padding:1rem;border-radius:12px;margin:.5rem 0}
</style>""",unsafe_allow_html=True)

@st.cache_resource
def charger_cnn():
    dossiers = [
        "/mount/src/pfe_agriculture_ia/models",
        os.path.join(ROOT, "models"),
        os.path.join(os.getcwd(), "models"),
        "models",
    ]
    CLASSES_DEF = ["Arachide_Malade","Arachide_Saine","Coton_Malade",
                   "Coton_Saine","Mais_Malade","Mais_Saine",
                   "Mil_Malade","Mil_Saine","Sorgho_Malade","Sorgho_Saine"]

    def load_cfg(d):
        cfg = os.path.join(d, "config_maladies.json")
        if os.path.exists(cfg):
            try: return json.load(open(cfg)).get("classes", CLASSES_DEF)
            except: pass
        return CLASSES_DEF

    for d in dossiers:
        p = os.path.join(d, "model_maladie.tflite")
        if not os.path.exists(p):
            continue
        # Méthode 1 : tflite-runtime (léger, sans TensorFlow)
        try:
            import tflite_runtime.interpreter as tflite
            interp = tflite.Interpreter(model_path=p)
            interp.allocate_tensors()
            return interp, load_cfg(d), True, "tflite"
        except ImportError:
            pass
        # Méthode 2 : tensorflow complet (si disponible)
        try:
            import tensorflow as tf
            interp = tf.lite.Interpreter(model_path=p)
            interp.allocate_tensors()
            return interp, load_cfg(d), True, "tflite"
        except ImportError:
            pass

    return None, CLASSES_DEF, False, "none"
model_cnn,CLASSES,CNN_OK,CNN_MODE=charger_cnn()

CONSEILS={
    "Mais_Malade":"Fongicide mancozèbe 2–3 kg/ha. Surveiller 7 jours.",
    "Mais_Saine":"Parcelle saine. Surveillance hebdomadaire.",
    "Sorgho_Malade":"Fongicide foliaire. Réduire l'humidité.",
    "Sorgho_Saine":"Parcelle saine. Suivi normal.",
    "Arachide_Malade":"Chlorothalonil 1.5 L/ha — 2 applications à 14j.",
    "Arachide_Saine":"Parcelle saine. Vérifier le sol.",
    "Mil_Malade":"Métalaxyl-M + mancozèbe recommandés.",
    "Mil_Saine":"Parcelle saine. Continuer le suivi.",
    "Coton_Malade":"Insecticide + fongicide. Consulter l'ITRAD.",
    "Coton_Saine":"Parcelle saine. Surveiller les parasites.",
}
SEUILS={"Mais":{"critique":0.25,"alerte":0.40},"Sorgho":{"critique":0.22,"alerte":0.38},
        "Arachide":{"critique":0.28,"alerte":0.42},"Mil":{"critique":0.20,"alerte":0.35},
        "Coton":{"critique":0.30,"alerte":0.45}}

def predire(img_pil):
    arr=np.expand_dims(np.array(img_pil.convert("RGB").resize((224,224)),dtype=np.float32)/255.0,0)
    if CNN_MODE=="tflite":
        i=model_cnn.get_input_details(); o=model_cnn.get_output_details()
        model_cnn.set_tensor(i[0]['index'],arr); model_cnn.invoke()
        return model_cnn.get_tensor(o[0]['index'])[0]
    return model_cnn.predict(arr,verbose=0)[0]

def score_ndvi(ndvi,culture,temp,humid,pluie):
    s=SEUILS.get(culture,{"critique":0.25,"alerte":0.40}); sc,r=0,[]
    if ndvi<s["critique"]:    sc+=4;r.append(f"NDVI très faible ({ndvi:.2f})")
    elif ndvi<s["alerte"]:    sc+=2;r.append(f"NDVI faible ({ndvi:.2f})")
    if temp>35:               sc+=1;r.append(f"T° élevée ({temp:.0f}°C)")
    if humid>75 and ndvi<0.4: sc+=1;r.append("Humidité → risque fongique")
    if pluie>50 and ndvi<0.4: sc+=1;r.append("Excès pluie → risque maladie")
    if sc>=4: return "Malade",min(90,60+sc*5),r
    if sc>=2: return "Stress",min(80,50+sc*5),r
    return "Saine",min(95,75+(5-sc)*3),r

def ndvi_camera(img_pil):
    arr=np.array(img_pil.convert("RGB").resize((224,224)),dtype=np.float32)/255.0
    R,G,B=arr[:,:,0],arr[:,:,1],arr[:,:,2]
    denom=G+R-B; denom[np.abs(denom)<0.001]=0.001
    vari=np.clip((G-R)/denom,-1,1); vari_moy=float(np.mean(vari))
    ndvi=round(max(-1.0,min(1.0,0.18+0.73*vari_moy)),3)
    etat="Saine" if ndvi>0.5 else "Stress" if ndvi>0.3 else "Malade"
    return {"ndvi_estime":ndvi,"vari":round(vari_moy,3),"etat":etat}

# HEADER
st.markdown("""
<div class="page-header" style="background:linear-gradient(135deg,#bf360c,#e65100)">
  <div style="font-size:2.2rem">🔬</div>
  <div><h1>Module Détection des Maladies</h1>
  <p>CNN MobileNetV2 · NDVI Sentinel-2 · Caméra smartphone · Météo temps réel · SQLite</p></div>
</div>""",unsafe_allow_html=True)

mode_txt="TFLite ✅" if CNN_MODE=="tflite" else "Keras ✅"
if CNN_OK:
    st.markdown(f'<div class="status-ok">✅ CNN MobileNetV2 chargé — Accuracy 52.27% (287 images tchadiennes) | {len(CLASSES)} classes | {mode_txt}</div>',unsafe_allow_html=True)
else:
    st.markdown('<div class="status-warn">📡 Mode NDVI actif — placez model_maladie.tflite dans models/</div>',unsafe_allow_html=True)

# MÉTÉO
st.markdown('<div class="meteo-box">',unsafe_allow_html=True)
st.markdown('<div class="meteo-title">🛰️ Météo temps réel — Open-Meteo</div>',unsafe_allow_html=True)
vc1,vc2=st.columns([3,1])
with vc1: ville_sel=st.selectbox("Ville",list(VILLES_TCHAD.keys()),label_visibility="collapsed")
with vc2: btn_m=st.button("🔄 Charger",use_container_width=True,type="primary")
if "meteo_mal" not in st.session_state: st.session_state.meteo_mal=None
if "ville_mal" not in st.session_state: st.session_state.ville_mal=ville_sel
if btn_m or st.session_state.ville_mal!=ville_sel:
    st.session_state.ville_mal=ville_sel
    with st.spinner(f"Météo {ville_sel}..."):
        c=VILLES_TCHAD[ville_sel]; st.session_state.meteo_mal=get_meteo_actuelle(c["lat"],c["lon"])
meteo=st.session_state.meteo_mal
if meteo and meteo.get("ok"):
    mc1,mc2,mc3,mc4,mc5=st.columns(5)
    mc1.metric("🌡️ T°",f"{meteo['temperature_moy']}°C")
    mc2.metric("💧 Hum.",f"{meteo['humidite_air']}%")
    mc3.metric("🌧️ Pluie",f"{meteo['pluie_7j']}mm")
    mc4.metric("💨 Vent",f"{meteo['vent_moy']}m/s")
    mc5.metric("☀️ ETP",f"{meteo['etp']}mm/j")
    st.caption(f"✅ {ville_sel} · {meteo['heure_maj']}")
else: st.caption("👆 Cliquez Charger")
st.markdown('</div>',unsafe_allow_html=True)

t_def=meteo["temperature_moy"] if meteo and meteo.get("ok") else 33.0
hu_def=meteo["humidite_air"] if meteo and meteo.get("ok") else 45.0
pl_def=meteo["pluie_7j"] if meteo and meteo.get("ok") else 10.0

# ONGLETS
lbl_cnn="📸 Analyse photo (CNN MobileNetV2)" if CNN_OK else "📸 Analyse photo (CNN — non chargé)"
tab_cnn,tab_ndvi,tab_cam=st.tabs([lbl_cnn,"🛰️ Analyse NDVI — Drone/Satellite","📷 NDVI Caméra Smartphone"])

# ── ONGLET CNN ─────────────────────────────────────────────────────
with tab_cnn:
    if not CNN_OK:
        st.info("🔄 Placez `model_maladie.tflite` dans `models/` pour activer.\n\nUtilisez les onglets 🛰️ **NDVI** ou 📷 **Caméra**.")
    else:
        st.markdown("### 📸 Diagnostic par photo de feuille")
        col_up,col_res=st.columns([1,1],gap="large")
        with col_up:
            st.markdown("""<div class="upload-guide">
                📷 <b>Protocole photo</b><br><br>
                ✅ Une feuille isolée · Fond blanc<br>
                ✅ Photo rapprochée (20–30 cm)<br>
                ✅ Lumière naturelle, sans flash<br><br>
                ❌ Pas de champ entier · Pas de fond complexe
            </div>""",unsafe_allow_html=True)
            photo=st.file_uploader("📁 Charger une photo (JPG, PNG)",
                                   type=["jpg","jpeg","png"],key="photo_cnn")
            if photo:
                img_orig=Image.open(photo)
                # Convertir RGBA/P en RGB
                if img_orig.mode in('RGBA','P','LA'):
                    img_orig=img_orig.convert('RGB')
                st.image(img_orig,caption=f"Photo : {photo.name}",
                         use_column_width=True)
        with col_res:
            if not photo:
                st.markdown("""<div style="background:white;border-radius:12px;
                     padding:3rem;text-align:center;color:#bbb;
                     box-shadow:0 2px 8px rgba(0,0,0,.05)">
                    <div style="font-size:3rem;margin-bottom:.5rem">🖼️</div>
                    <div>Chargez une photo<br>pour lancer le diagnostic</div>
                </div>""",unsafe_allow_html=True)
            else:
                if st.button("🔍 Analyser la feuille",type="primary",
                             use_container_width=True,key="btn_cnn"):
                    with st.spinner("Analyse CNN en cours..."):
                        preds=predire(img_orig)
                        idx=int(np.argmax(preds))
                        conf=float(preds[idx])*100
                        cls=CLASSES[idx] if idx<len(CLASSES) else f"Classe {idx}"
                    parts=cls.split("_")
                    culture=parts[0] if parts else "?"
                    etat=parts[1] if len(parts)>1 else "?"
                    conseil=CONSEILS.get(cls,"Consultez un agronome.")
                    style="result-malade" if etat=="Malade" else "result-sain"
                    icon="🦠" if etat=="Malade" else "✅"
                    st.markdown(f'<div class="{style}">{icon} {culture} — {etat.upper()}</div>',unsafe_allow_html=True)
                    rc1,rc2=st.columns(2)
                    rc1.metric("Confiance",f"{conf:.1f}%")
                    rc2.metric("Culture",culture)
                    if conf>95:
                        st.warning("⚠️ Vérifiez que la photo montre une feuille isolée sur fond neutre.")
                    if meteo and meteo.get("ok"):
                        st.info(f"📍 {ville_sel} : T°={meteo['temperature_moy']}°C | Hum={meteo['humidite_air']}% | Pluie={meteo['pluie_7j']}mm")
                    st.markdown(f'<div class="conseil">💊 <b>Traitement recommandé :</b><br>{conseil}</div>',unsafe_allow_html=True)
                    with st.expander("📊 Toutes les probabilités"):
                        for i in np.argsort(preds)[::-1][:5]:
                            c=CLASSES[i] if i<len(CLASSES) else f"Classe {i}"
                            prb=float(preds[i]); clr="#e53935" if "Malade" in c else "#27ae60"
                            ico="🔴" if "Malade" in c else "🟢"
                            st.markdown(
                                f'<div class="prob-row"><span style="width:160px;font-size:.8rem">{ico} {c}</span>'
                                f'<div class="prob-bg"><div class="prob-fill" style="width:{prb*100:.1f}%;background:{clr}"></div></div>'
                                f'<span class="prob-val">{prb*100:.1f}%</span></div>',unsafe_allow_html=True)
                    try:
                        sauvegarder_maladie(ville=ville_sel,culture=culture,methode="CNN Photo",
                            resultat=cls,etat=etat,confiance=conf,
                            temperature=meteo.get("temperature_moy") if meteo and meteo.get("ok") else None,
                            humidite_air=meteo.get("humidite_air") if meteo and meteo.get("ok") else None,
                            pluie_7j=meteo.get("pluie_7j") if meteo and meteo.get("ok") else None,
                            traitement=conseil)
                        st.success("💾 Sauvegardé dans l'historique")
                    except Exception: pass
                    st.caption(f"CNN MobileNetV2 | Dataset tchadien 287 images | Accuracy 52.27% | {mode_txt}")

# ── ONGLET NDVI ────────────────────────────────────────────────────
with tab_ndvi:
    st.markdown("### 🛰️ Diagnostic NDVI — Drone ou Satellite")
    nd1,nd2=st.columns([1,1],gap="large")
    with nd1:
        st.markdown("""
        <div class="drone-card" style="background:linear-gradient(135deg,#e3f2fd,#bbdefb);border-left:4px solid #1565c0">
            <b style="color:#0d47a1">🚁 Drone multispectral</b><br>
            Survole la parcelle → NDVI/EVI/SAVI calculés. Résolution 5–10 cm/pixel.<br>
            <em>Logiciels : Pix4D, DroneDeploy, Agisoft</em>
        </div>
        <div class="drone-card" style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9);border-left:4px solid #27ae60">
            <b style="color:#1b5e20">🛰️ Satellite Sentinel-2 (gratuit ESA)</b><br>
            Couvre le Tchad tous les 5 jours. Résolution 10m.<br>
            1. Aller sur <b>apps.sentinel-hub.com/eo-browser</b><br>
            2. Chercher votre parcelle → sélectionner "NDVI"<br>
            3. Lire la valeur et l'entrer ci-dessous
        </div>
        <div class="drone-card" style="background:linear-gradient(135deg,#f3e5f5,#e1bee7);border-left:4px solid #7b1fa2">
            <b style="color:#4a148c">📱 Estimation visuelle</b><br>
            Feuilles vertes denses → NDVI ≈ 0.65–0.80 🟢<br>
            Feuilles vertes pâles → NDVI ≈ 0.35–0.50 🟡<br>
            Jaunissement partiel → NDVI ≈ 0.15–0.30 🔴
        </div>""",unsafe_allow_html=True)
    with nd2:
        if meteo and meteo.get("ok"): st.success(f"✅ Météo pré-remplie — {ville_sel}")
        st.markdown("""<div class="ndvi-legend">
            <div class="nl-r">🔴 Malade (&lt;0.3)</div>
            <div class="nl-y">🟡 Stress (0.3–0.5)</div>
            <div class="nl-g">🟢 Sain (&gt;0.5)</div>
        </div>""",unsafe_allow_html=True)
        ndvi=st.slider("**NDVI**",-1.0,1.0,0.62,0.01)
        if ndvi>0.5:   st.success(f"🟢 NDVI={ndvi:.2f} — Sain")
        elif ndvi>0.3: st.warning(f"🟡 NDVI={ndvi:.2f} — Stress modéré")
        else:          st.error(f"🔴 NDVI={ndvi:.2f} — Stress sévère")
        evi=st.slider("**EVI**",-1.0,1.0,0.50,0.01)
        savi=st.slider("**SAVI**",-1.0,1.0,0.55,0.01,help="Adapté zones semi-arides (Sahel)")
        st.markdown("---")
        n1,n2=st.columns(2)
        with n1:
            temperature=st.number_input("Température (°C)",15.0,45.0,float(t_def),0.5)
            pluie_nd=st.number_input("Pluie 7j (mm)",0.0,300.0,float(pl_def),1.0)
        with n2:
            humidite_nd=st.number_input("Humidité (%)",10.0,95.0,float(hu_def),1.0)
            culture_nd=st.selectbox("🌾 Culture",["Mais","Sorgho","Arachide","Mil","Coton"],key="cult_nd")
        zone_auto=VILLES_TCHAD.get(ville_sel,{}).get("zone","Sahélienne")
        zone_nd=st.radio("Zone",["Sahélienne","Soudanienne"],
                         index=0 if zone_auto=="Sahélienne" else 1,horizontal=True,key="zone_nd")
        if st.button("🔍 Analyser (NDVI)",type="primary",use_container_width=True,key="btn_ndvi"):
            niveau,conf,raisons=score_ndvi(ndvi,culture_nd,temperature,humidite_nd,pluie_nd)
            conseil=CONSEILS.get(f"{culture_nd}_{niveau}","Consultez un agronome.")
            style=("result-malade" if niveau=="Malade" else "result-sain" if niveau=="Saine" else "result-stress")
            icon="🦠" if niveau=="Malade" else "✅" if niveau=="Saine" else "⚠️"
            st.markdown(f'<div class="{style}">{icon} {culture_nd} — {niveau.upper()}</div>',unsafe_allow_html=True)
            nr1,nr2,nr3=st.columns(3)
            nr1.metric("Confiance",f"{conf:.0f}%"); nr2.metric("NDVI",f"{ndvi:.3f}"); nr3.metric("Zone",zone_nd)
            st.markdown(f'<div class="conseil">💊 <b>Traitement :</b> {conseil}</div>',unsafe_allow_html=True)
            if meteo and meteo.get("ok"):
                st.success(f"📍 {ville_sel} : T°={temperature}°C | Hum={humidite_nd}% | Pluie={pluie_nd}mm")
            if raisons:
                with st.expander("🔍 Facteurs de risque"):
                    for r in raisons: st.markdown(f"• {r}")
            with st.expander("📋 Seuils NDVI par culture"):
                st.markdown("""
| Culture | 🔴 Malade | 🟡 Stress | 🟢 Sain |
|---------|-----------|-----------|---------|
| 🌽 Maïs | < 0.25 | 0.25–0.40 | > 0.40 |
| 🌾 Sorgho | < 0.22 | 0.22–0.38 | > 0.38 |
| 🥜 Arachide | < 0.28 | 0.28–0.42 | > 0.42 |
| 🌾 Mil | < 0.20 | 0.20–0.35 | > 0.35 |
| 🌿 Coton | < 0.30 | 0.30–0.45 | > 0.45 |""")
            try:
                sauvegarder_maladie(ville=ville_sel,culture=culture_nd,methode="NDVI Télédétection",
                    resultat=f"{culture_nd}_{niveau}",etat=niveau,confiance=conf,ndvi=ndvi,
                    temperature=temperature,humidite_air=humidite_nd,pluie_7j=pluie_nd,traitement=conseil)
                st.success("💾 Sauvegardé dans l'historique")
            except Exception: pass

# ── ONGLET CAMÉRA ──────────────────────────────────────────────────
with tab_cam:
    st.markdown("### 📷 NDVI estimé depuis caméra smartphone")
    st.markdown("""<div class="drone-card" style="background:linear-gradient(135deg,#f3e5f5,#e1bee7);border-left:4px solid #7b1fa2">
        <b style="color:#4a148c">📷 Principe VARI (Visible Atmospherically Resistant Index)</b><br>
        Votre smartphone n'a pas de capteur NIR. On utilise VARI = (G - R) / (G + R - B)
        qui corrèle avec le NDVI pour les zones agricoles.<br>
        <b>NDVI estimé ≈ 0.18 + 0.73 × VARI</b><br>
        ⚠️ Estimation approximative — moins précis qu'un satellite ou drone.
    </div>""",unsafe_allow_html=True)
    col_c1,col_c2=st.columns([1,1],gap="large")
    with col_c1:
        st.info("📸 Conseils :\n- Photographiez une feuille représentative\n- Fond blanc ou ciel\n- Bonne luminosité naturelle\n- Image nette et bien exposée")
        photo_cam=st.file_uploader("📁 Photo de la plante",type=["jpg","jpeg","png"],key="photo_cam")
        if photo_cam:
            img_cam=Image.open(photo_cam)
            if img_cam.mode in('RGBA','P','LA'): img_cam=img_cam.convert('RGB')
            st.image(img_cam,caption="Photo chargée",use_column_width=True)
    with col_c2:
        if not photo_cam:
            st.markdown("""<div style="background:white;border-radius:12px;padding:3rem;
                 text-align:center;color:#bbb">
                <div style="font-size:3rem">📷</div>
                Chargez une photo pour estimer le NDVI</div>""",unsafe_allow_html=True)
        else:
            culture_cam=st.selectbox("🌾 Culture",["Mais","Sorgho","Arachide","Mil","Coton"],key="cult_cam")
            if st.button("📊 Estimer le NDVI",type="primary",use_container_width=True,key="btn_cam"):
                with st.spinner("Analyse VARI → NDVI..."):
                    res=ndvi_camera(img_cam)
                ndvi_val=res["ndvi_estime"]; vari_val=res["vari"]; etat_cam=res["etat"]
                clr="#27ae60" if ndvi_val>0.5 else "#ff9800" if ndvi_val>0.3 else "#e53935"
                st.markdown(
                    f'<div class="ndvi-result" style="background:{clr}20;border:2px solid {clr};color:{clr}">'
                    f'NDVI estimé = {ndvi_val}</div>',unsafe_allow_html=True)
                nc1,nc2=st.columns(2)
                nc1.metric("NDVI estimé",ndvi_val); nc2.metric("VARI",vari_val)
                niveau,conf,raisons=score_ndvi(ndvi_val,culture_cam,t_def,hu_def,pl_def)
                conseil=CONSEILS.get(f"{culture_cam}_{niveau}","Consultez un agronome.")
                style=("result-malade" if niveau=="Malade" else "result-sain" if niveau=="Saine" else "result-stress")
                icon="🦠" if niveau=="Malade" else "✅" if niveau=="Saine" else "⚠️"
                st.markdown(f'<div class="{style}">{icon} {culture_cam} — {niveau.upper()}</div>',unsafe_allow_html=True)
                st.markdown(f'<div class="conseil">💊 {conseil}</div>',unsafe_allow_html=True)
                with st.expander("🎨 Analyse colorimétrique"):
                    arr=np.array(img_cam.convert("RGB").resize((224,224)),dtype=np.float32)/255.0
                    st.markdown(f"""
| Canal | Valeur moyenne | Rôle |
|-------|----------------|------|
| 🔴 Rouge | {arr[:,:,0].mean():.3f} | Absorption chlorophylle |
| 🟢 Vert | {arr[:,:,1].mean():.3f} | Réflexion végétation |
| 🔵 Bleu | {arr[:,:,2].mean():.3f} | Réflexion atmosphère |""")
                st.warning("⚠️ Estimation approximative — pour mesure précise utilisez Sentinel-2.")
                try:
                    sauvegarder_maladie(ville=ville_sel,culture=culture_cam,methode="NDVI Caméra (VARI)",
                        resultat=f"{culture_cam}_{niveau}",etat=niveau,confiance=conf,ndvi=ndvi_val,
                        temperature=t_def,humidite_air=hu_def,pluie_7j=pl_def,traitement=conseil)
                    st.success("💾 Sauvegardé dans l'historique")
                except Exception: pass

st.divider()
st.warning("⚠️ Outil d'aide à la décision. Consultez un agronome ou l'**ITRAD** pour validation.")
st.caption("CNN MobileNetV2 | Dataset tchadien 287 images | Acc. 52.27% | Sentinel-2 ESA | VARI smartphone | Météo Open-Meteo")
