import streamlit as st
import numpy as np
import joblib, os, sys

st.set_page_config(page_title="Irrigation",page_icon="💧",layout="wide",initial_sidebar_state="expanded")
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path: sys.path.insert(0,ROOT)
from styles import GLOBAL_CSS
from meteo_api import VILLES_TCHAD, get_meteo_actuelle
from database import sauvegarder_irrigation

st.markdown(GLOBAL_CSS,unsafe_allow_html=True)
st.markdown("""<style>[data-testid="stAppViewContainer"]{background:linear-gradient(160deg,#e3f2fd 0%,#e8f5e9 100%)}</style>""",unsafe_allow_html=True)

@st.cache_resource
def charger():
    for base in [os.path.join(ROOT,"models"),os.path.join(os.getcwd(),"models"),"models"]:
        try:
            return joblib.load(os.path.join(base,"model_irrigation.pkl")),\
                   joblib.load(os.path.join(base,"scaler_irrigation.pkl")),True
        except Exception: continue
    return None,None,False

model_irr,scaler_irr,ok=charger()

st.markdown("""
<div class="page-header" style="background:linear-gradient(135deg,#0d47a1,#1976d2)">
  <div style="font-size:2.2rem">💧</div>
  <div><h1>Module Irrigation</h1>
  <p>Random Forest · Accuracy 78.51% · AUC-ROC 0.8782 · F1 72.57% · CV 78.87% · 16 435 obs. NASA POWER</p></div>
</div>""",unsafe_allow_html=True)

if not ok:
    st.error("⚠️ Modèle non trouvé — placez model_irrigation.pkl dans models/")
    st.stop()

# Météo
st.markdown('<div class="meteo-box">',unsafe_allow_html=True)
st.markdown('<div class="meteo-title">🛰️ Météo temps réel — Open-Meteo</div>',unsafe_allow_html=True)
vc1,vc2=st.columns([3,1])
with vc1: ville_sel=st.selectbox("Ville",list(VILLES_TCHAD.keys()),label_visibility="collapsed")
with vc2: btn_m=st.button("🔄 Charger",use_container_width=True,type="primary")
if "meteo_irr" not in st.session_state: st.session_state.meteo_irr=None
if "ville_irr" not in st.session_state: st.session_state.ville_irr=ville_sel
if btn_m or st.session_state.ville_irr!=ville_sel:
    st.session_state.ville_irr=ville_sel
    with st.spinner(f"Météo {ville_sel}..."):
        c=VILLES_TCHAD[ville_sel]; st.session_state.meteo_irr=get_meteo_actuelle(c["lat"],c["lon"])
meteo=st.session_state.meteo_irr
if meteo and meteo.get("ok"):
    mc1,mc2,mc3,mc4,mc5=st.columns(5)
    mc1.metric("🌡️ T°",f"{meteo['temperature_moy']}°C")
    mc2.metric("💧 Hum.",f"{meteo['humidite_air']}%")
    mc3.metric("🌧️ Pluie 7j",f"{meteo['pluie_7j']}mm")
    mc4.metric("💨 Vent",f"{meteo['vent_moy']}m/s")
    mc5.metric("☀️ ETP",f"{meteo['etp']}mm/j")
    st.caption(f"✅ {ville_sel} · {meteo['heure_maj']}")
else: st.caption("👆 Cliquez Charger pour météo temps réel")
st.markdown('</div>',unsafe_allow_html=True)

t_def=meteo["temperature_moy"] if meteo and meteo.get("ok") else 34.0
tm_def=meteo["temperature_max"] if meteo and meteo.get("ok") else 41.0
hu_def=meteo["humidite_air"] if meteo and meteo.get("ok") else 30.0
p7_def=meteo["pluie_7j"] if meteo and meteo.get("ok") else 5.0
p14_def=meteo["pluie_14j"] if meteo and meteo.get("ok") else 9.0
v_def=meteo["vent_moy"] if meteo and meteo.get("ok") else 3.0
r_def=meteo["rayonnement"] if meteo and meteo.get("ok") else 22.0
etp_def=meteo["etp"] if meteo and meteo.get("ok") else 7.0
sol_def=meteo["humidite_sol"] if meteo and meteo.get("ok") else 20.0

if meteo and meteo.get("ok"): st.success("✅ Formulaire pré-rempli depuis Open-Meteo")
st.markdown("### 📥 Paramètres de la parcelle")
col1,col2,col3=st.columns(3,gap="medium")

with col1:
    st.markdown('<div class="card"><div class="card-title">🌡️ Données climatiques</div>',unsafe_allow_html=True)
    temperature_moy=st.slider("Température moyenne (°C)",15.0,45.0,float(t_def),0.5)
    temperature_max=st.slider("Température maximale (°C)",20.0,52.0,float(min(tm_def,52.0)),0.5)
    pluie_7j=st.number_input("Pluie 7 jours (mm)",0.0,250.0,float(p7_def),1.0)
    pluie_14j=st.number_input("Pluie 14 jours (mm)",0.0,400.0,float(p14_def),1.0)
    humidite_air=st.slider("Humidité air (%)",5.0,95.0,float(hu_def),1.0)
    vent_moy=st.slider("Vent (m/s)",0.0,15.0,float(min(v_def,15.0)),0.5)
    rayonnement=st.slider("Rayonnement (MJ/m²/j)",5.0,35.0,float(min(r_def,35.0)),0.5)
    st.markdown('</div>',unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-title">🌱 Sol et culture</div>',unsafe_allow_html=True)
    humidite_sol=st.slider("Humidité sol (%)",5.0,90.0,float(min(sol_def,90.0)),1.0)
    etp=st.slider("ETP (mm/j)",2.0,14.0,float(min(etp_def,14.0)),0.1)
    ph_sol=st.slider("pH du sol",5.0,9.0,7.0,0.1)
    culture=st.selectbox("Culture",["Mil","Sorgho","Arachide","Mais","Coton"])
    culture_enc={"Arachide":0,"Coton":1,"Mais":2,"Mil":3,"Sorgho":4}[culture]
    stade=st.selectbox("Stade phénologique",["Semis","Levée","Floraison","Maturation","Repos"],index=2)
    stade_enc={"Floraison":0,"Levée":1,"Maturation":2,"Repos":3,"Semis":4}[stade]
    st.markdown('</div>',unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card"><div class="card-title">🗺️ Zone et saison</div>',unsafe_allow_html=True)
    zone_auto=VILLES_TCHAD.get(ville_sel,{}).get("zone","Sahélienne")
    zone=st.selectbox("Zone",["Sahélienne","Soudanienne"],index=0 if zone_auto=="Sahélienne" else 1)
    zone_enc=0 if zone=="Sahélienne" else 1
    saison=st.selectbox("Saison",["Sèche","Début des pluies","Saison des pluies"])
    saison_enc={"Début des pluies":0,"Saison des pluies":1,"Sèche":2}[saison]
    type_sol=st.selectbox("Type de sol",["Argileux","Limoneux","Sableux"],index=2)
    sol_enc={"Argileux":0,"Limoneux":1,"Sableux":2}[type_sol]
    st.markdown(f'<div style="background:#f0f4f8;border-radius:8px;padding:.8rem;font-size:.82rem;margin-top:.5rem;line-height:1.8">🌾 <b>{culture}</b> · {stade}<br>🗺️ {zone} · {saison}<br>📍 {ville_sel}</div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

st.markdown("---")
if st.button("🔍 Analyser le besoin en irrigation",type="primary",use_container_width=True):
    X=np.array([[temperature_moy,temperature_max,pluie_7j,pluie_14j,
                 humidite_air,humidite_sol,etp,vent_moy,rayonnement,
                 culture_enc,stade_enc,saison_enc,sol_enc,ph_sol,zone_enc]])
    Xs=scaler_irr.transform(X)
    pred=model_irr.predict(Xs)[0]
    proba=model_irr.predict_proba(Xs)[0]
    conf=proba[pred]*100
    dose=round(max(0,40-humidite_sol)*0.5+etp*1.8,1) if pred==1 else 0
    resultat_txt="OUI" if pred==1 else "NON"

    st.markdown("### 📊 Résultat")
    if pred==1:
        st.markdown(f'<div class="result-irr">💧 IRRIGATION RECOMMANDÉE — Dose : {dose} mm</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="conseil">🌾 <b>{culture}</b> en <b>{stade}</b> à <b>{ville_sel}</b> nécessite une irrigation.<br>⏰ Créneau optimal : <b>5h–8h du matin</b> (limite l\'évaporation).</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="result-no-irr">✅ IRRIGATION NON NÉCESSAIRE</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="conseil"><b>{culture}</b> à <b>{ville_sel}</b> dispose de suffisamment d\'humidité.<br>📅 Prochaine vérification dans 3–5 jours.</div>',unsafe_allow_html=True)

    rc1,rc2,rc3=st.columns(3)
    rc1.metric("Confiance",f"{conf:.1f}%")
    rc2.metric("P(OUI)",f"{proba[1]*100:.1f}%")
    rc3.metric("P(NON)",f"{proba[0]*100:.1f}%")

    with st.expander("ℹ️ Informations du modèle"):
        st.markdown("""
        | Métrique | Valeur |
        |---|---|
        | Accuracy (test) | **78.51%** |
        | Précision | 68.59% |
        | Rappel | 77.03% |
        | F1-Score | **72.57%** |
        | AUC-ROC | **0.8782** |
        | CV Score (k=5) | 78.87% |
        | Observations | 16 435 (NASA POWER) |
        | Top variable | humidite_air (0.124) |
        """)

    try:
        sauvegarder_irrigation(ville=ville_sel,culture=culture,stade=stade,zone=zone,
            saison=saison,type_sol=type_sol,temperature_moy=temperature_moy,
            humidite_air=humidite_air,pluie_7j=pluie_7j,humidite_sol=humidite_sol,
            etp=etp,resultat=resultat_txt,dose_mm=dose,confiance=conf)
        st.success("💾 Analyse sauvegardée dans l'historique")
    except Exception as e:
        st.warning(f"⚠️ Sauvegarde : {e}")

    src="Open-Meteo" if meteo and meteo.get("ok") else "Manuel"
    st.caption(f"Random Forest · Météo: {src} · Accuracy: 78.51% · AUC: 0.8782")
