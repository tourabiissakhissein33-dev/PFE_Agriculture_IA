import streamlit as st
import numpy as np
import joblib, os, sys

st.set_page_config(page_title="Fertilisation", page_icon="🌿",
                   layout="wide", initial_sidebar_state="expanded")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from styles import GLOBAL_CSS
from meteo_api import VILLES_TCHAD, get_meteo_actuelle

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""<style>
[data-testid="stAppViewContainer"]{
    background:linear-gradient(160deg,#e8f5e9 0%,#f1f8e9 100%);
}
</style>""", unsafe_allow_html=True)

@st.cache_resource
def charger():
    for base in [os.path.join(ROOT,"models"),
                 os.path.join(os.getcwd(),"models"),"models"]:
        try:
            return (
                joblib.load(os.path.join(base,"model_fertilisation.pkl")),
                joblib.load(os.path.join(base,"scaler_fertilisation.pkl")),
                joblib.load(os.path.join(base,"label_encoder_engrais.pkl")),
                joblib.load(os.path.join(base,"label_encoder_culture.pkl")),
                joblib.load(os.path.join(base,"label_encoder_sol.pkl")),
                True)
        except Exception:
            continue
    return None,None,None,None,None,False

model_f,scaler_f,le_eng,le_cult,le_sol,ok = charger()

ENGRAIS = {
    "Uree":        ("Uree 46-0-0",  "50-100 kg/ha","Semis + 30j apres levee","#1565c0"),
    "DAP":         ("DAP 18-46-0",  "50-75 kg/ha", "Au semis uniquement",    "#1b5e20"),
    "NPK_15_15_15":("NPK 15-15-15", "100-150 kg/ha","Au semis",              "#4a148c"),
    "NPK_23_10_5": ("NPK 23-10-5",  "100-200 kg/ha","Semis + couverture 30j","#bf360c"),
    "KCl":         ("KCl 0-0-60",   "30-50 kg/ha", "Au semis",              "#e65100"),
}

st.markdown("""
<div class="page-header" style="background:linear-gradient(135deg,#1b5e20,#27ae60)">
  <div style="font-size:2.2rem">🌿</div>
  <div>
    <h1>Module Fertilisation</h1>
    <p>Recommandation engrais · XGBoost · Accuracy 95.42% · F1 95.47%</p>
  </div>
</div>""", unsafe_allow_html=True)

if not ok:
    st.error("Modele non trouve — placez les fichiers .pkl dans models/")
    st.stop()

# METEO
st.markdown('<div class="meteo-box">', unsafe_allow_html=True)
st.markdown('<div class="meteo-title">🛰️ Conditions climatiques temps réel (Open-Meteo) — pre-remplit temperature, humidite et pluie</div>', unsafe_allow_html=True)

vc1,vc2 = st.columns([3,1])
with vc1:
    ville_sel = st.selectbox("Ville",list(VILLES_TCHAD.keys()),label_visibility="collapsed")
with vc2:
    btn_m = st.button("🔄 Charger",use_container_width=True,type="primary")

if "meteo_fert" not in st.session_state: st.session_state.meteo_fert = None
if "ville_fert" not in st.session_state: st.session_state.ville_fert = ville_sel

if btn_m or st.session_state.ville_fert != ville_sel:
    st.session_state.ville_fert = ville_sel
    with st.spinner(f"Chargement meteo {ville_sel}..."):
        c = VILLES_TCHAD[ville_sel]
        st.session_state.meteo_fert = get_meteo_actuelle(c["lat"],c["lon"])

meteo = st.session_state.meteo_fert
if meteo and meteo.get("ok"):
    mc1,mc2,mc3,mc4 = st.columns(4)
    mc1.metric("Température", f"{meteo['temperature_moy']}°C")
    mc2.metric("Humidité air", f"{meteo['humidite_air']}%")
    mc3.metric("Pluie 7j",    f"{meteo['pluie_7j']} mm")
    mc4.metric("Vent",        f"{meteo['vent_moy']} m/s")
    st.caption(f"✅ {ville_sel} · {meteo['heure_maj']} · Open-Meteo (cache 30 min)")
elif meteo and not meteo.get("ok"):
    st.warning(f"Meteo indisponible : {meteo.get('erreur')}")
else:
    st.caption("Cliquez Charger pour pre-remplir la temperature et l'humidite")

st.markdown('</div>', unsafe_allow_html=True)

st.info("La temperature et l'humidite influencent l'absorption des nutriments par les racines et la volatilisation de l'azote (Uree). Ces donnees ameliorent la precision de la recommandation.")

t_def  = meteo["temperature_moy"] if meteo and meteo.get("ok") else 30.0
hu_def = meteo["humidite_air"]    if meteo and meteo.get("ok") else 55.0
pl_def = meteo["pluie_7j"]        if meteo and meteo.get("ok") else 50.0

if meteo and meteo.get("ok"):
    st.success("✅ Temperature, humidite et pluie pre-remplies depuis Open-Meteo")

st.markdown("### 📥 Analyse de la parcelle")
col1,col2,col3 = st.columns(3,gap="medium")

with col1:
    st.markdown('<div class="card"><div class="card-title">Analyse NPK du sol</div>', unsafe_allow_html=True)
    st.caption("Valeurs issues d'une analyse de sol (kg/ha)")
    N  = st.number_input("Azote N (kg/ha)",0.0,200.0,20.0,1.0)
    P  = st.number_input("Phosphore P (kg/ha)",0.0,100.0,10.0,1.0)
    K  = st.number_input("Potassium K (kg/ha)",0.0,100.0,15.0,1.0)
    ph = st.slider("pH du sol",5.0,9.0,6.8,0.1)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    label_meteo = "✅ Open-Meteo" if meteo and meteo.get("ok") else "⬆️ Charger meteo"
    st.markdown(f'<div class="card"><div class="card-title">Conditions climatiques &nbsp;<span style="color:#27ae60;font-weight:400;text-transform:none">{label_meteo}</span></div>', unsafe_allow_html=True)
    temperature  = st.slider("Temperature (°C)",15.0,45.0,float(t_def),0.5)
    humidite_air = st.slider("Humidite air (%)",10.0,95.0,float(hu_def),1.0)
    humidite_sol = st.slider("Humidite sol (%)",5.0,90.0,40.0,1.0)
    pluie = st.number_input("Pluie recente (mm)",0.0,300.0,float(pl_def),5.0)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card"><div class="card-title">Culture et sol</div>', unsafe_allow_html=True)
    culture  = st.selectbox("Culture",["Mil","Sorgho","Arachide","Mais","Coton"])
    type_sol = st.selectbox("Type de sol",["Argileux","Limoneux","Sableux"],index=1)
    zone_auto = VILLES_TCHAD.get(ville_sel,{}).get("zone","Sahelienne")
    zone = st.selectbox("Zone",["Sahelienne","Soudanienne"],
                        index=0 if zone_auto=="Sahélienne" else 1)
    zone_enc = 0 if "Sahel" in zone else 1
    try:
        cult_enc = le_cult.transform([culture])[0]
        sol_enc  = le_sol.transform([type_sol])[0]
    except Exception:
        cult_enc = 0; sol_enc = 1
    st.markdown(f"""
    <div style="background:#f0f4f0;border-radius:8px;padding:.8rem;
         font-size:.82rem;color:#333;margin-top:.5rem;line-height:1.8">
        🌾 <b>{culture}</b> · Sol {type_sol}<br>
        🗺️ Zone {zone} · 📍 {ville_sel}
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

if st.button("🔍 Recommander un engrais", type="primary", use_container_width=True):
    X  = np.array([[N,K,P,temperature,humidite_air,humidite_sol,ph,pluie,cult_enc,sol_enc,zone_enc]])
    Xs = scaler_f.transform(X)
    pred    = model_f.predict(Xs)[0]
    proba   = model_f.predict_proba(Xs)[0]
    engrais = le_eng.inverse_transform([pred])[0]
    conf    = proba[pred]*100
    info    = ENGRAIS.get(engrais,("","","","#1a5276"))

    st.markdown("### 📊 Resultat")
    col_r1,col_r2 = st.columns([2,1],gap="large")

    with col_r1:
        cl = info[3]
        st.markdown(
            f'<div style="background:white;border-left:5px solid {cl};'
            f'border-radius:12px;padding:1.3rem;box-shadow:0 2px 10px rgba(0,0,0,.07);margin-bottom:.8rem">'
            f'<div style="font-size:1.3rem;font-weight:800;color:{cl};margin-bottom:.4rem">🌿 {engrais}</div>'
            f'<div style="font-size:.9rem;color:#555;margin-bottom:.6rem">{info[0]}</div>'
            f'<div style="font-size:.84rem;line-height:1.8;color:#333">'
            f'📏 <b>Dose :</b> {info[1]}<br>'
            f'⏰ <b>Moment :</b> {info[2]}</div></div>',
            unsafe_allow_html=True)
        if meteo and meteo.get("ok"):
            st.markdown(
                f'<div class="conseil" style="border-color:#27ae60">'
                f'🛰️ <b>Contexte meteo ({ville_sel}) :</b> '
                f'T={meteo["temperature_moy"]}C · '
                f'Humidite={meteo["humidite_air"]}% · '
                f'Pluie 7j={meteo["pluie_7j"]}mm<br>'
                f'<span style="color:#555;font-size:.82rem">'
                f'Ces conditions ont influence la recommandation.</span></div>',
                unsafe_allow_html=True)

    with col_r2:
        st.metric("Confiance", f"{conf:.1f}%")
        st.metric("Culture",   culture)
        st.metric("Sol",       type_sol)
        st.metric("Meteo", "Open-Meteo ✅" if meteo and meteo.get("ok") else "Manuel")

    with st.expander("Probabilites par engrais"):
        for cls,p in zip(le_eng.classes_,proba):
            cl_c = ENGRAIS.get(cls,("","","","#888"))[3]
            st.markdown(
                f'<div class="prob-row">'
                f'<span style="width:130px;font-size:.8rem">🌿 {cls}</span>'
                f'<div class="prob-bg"><div class="prob-fill" '
                f'style="width:{p*100:.1f}%;background:{cl_c}"></div></div>'
                f'<span class="prob-val">{p*100:.1f}%</span></div>',
                unsafe_allow_html=True)

    src = "Open-Meteo temps reel" if meteo and meteo.get("ok") else "Saisie manuelle"
    st.caption(f"Modele : XGBoost | Meteo : {src} | Accuracy : 95.42% | F1 : 95.47%")