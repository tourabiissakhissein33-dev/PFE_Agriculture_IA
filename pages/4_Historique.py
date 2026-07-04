import streamlit as st
import pandas as pd
import os, sys
from datetime import datetime

st.set_page_config(page_title="Historique",page_icon="📋",layout="wide",initial_sidebar_state="expanded")
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path: sys.path.insert(0,ROOT)
from styles import GLOBAL_CSS
from database import (lire_historique_irrigation,lire_historique_fertilisation,
    lire_historique_maladies,lire_tout_historique,statistiques,vider_historique)

st.markdown(GLOBAL_CSS,unsafe_allow_html=True)
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:linear-gradient(160deg,#f3e5f5 0%,#e8eaf6 100%)}
</style>""",unsafe_allow_html=True)

st.markdown("""
<div class="page-header" style="background:linear-gradient(135deg,#4a148c,#7b1fa2)">
  <div style="font-size:2.2rem">📋</div>
  <div><h1>Historique des Analyses</h1>
  <p>Toutes les analyses sauvegardées · Export CSV · Statistiques · Base SQLite</p></div>
</div>""",unsafe_allow_html=True)

try: stats=statistiques()
except Exception: stats={"total":0,"n_irrigation":0,"n_fertilisation":0,"n_maladies":0,
    "top_culture":"—","zone_risque":"—","taux_irrigation":0,"taux_maladie":0}

if stats["total"]==0:
    st.info("📭 Aucune analyse enregistrée.\n\nEffectuez des analyses dans les modules Irrigation, Fertilisation ou Maladies — elles seront automatiquement sauvegardées ici.")
else:
    # Métriques
    c1,c2,c3,c4=st.columns(4)
    for col,val,lbl,clr in [
        (c1,stats["total"],"📋 Total analyses","#4a148c"),
        (c2,stats["n_irrigation"],"💧 Irrigation","#1565c0"),
        (c3,stats["n_fertilisation"],"🌿 Fertilisation","#27ae60"),
        (c4,stats["n_maladies"],"🔬 Maladies","#e65100"),
    ]:
        col.markdown(f'<div class="metric-card" style="border-color:{clr}"><div class="metric-val" style="color:{clr}">{val}</div><div class="metric-lbl">{lbl}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    s1,s2,s3,s4=st.columns(4)
    s1.metric("🌾 Culture + analysée",stats["top_culture"])
    s2.metric("📍 Zone à risque",stats["zone_risque"])
    s3.metric("💧 Taux irrigation OUI",f"{stats['taux_irrigation']}%")
    s4.metric("🦠 Taux maladies détec.",f"{stats['taux_maladie']}%")
    st.markdown("<br>",unsafe_allow_html=True)

    # Export
    st.markdown("### 📥 Export CSV")
    ex1,ex2,ex3,ex4=st.columns(4)
    for col,fn,lbl,module in [
        (ex1,lire_historique_irrigation,"💧 Irrigation CSV","irrigation"),
        (ex2,lire_historique_fertilisation,"🌿 Fertilisation CSV","fertilisation"),
        (ex3,lire_historique_maladies,"🔬 Maladies CSV","maladies"),
    ]:
        try:
            df=pd.DataFrame(fn(1000))
            if not df.empty:
                csv=df.to_csv(index=False).encode("utf-8")
                col.download_button(lbl,csv,f"{module}_{datetime.now().strftime('%Y%m%d')}.csv","text/csv",use_container_width=True)
        except Exception: col.caption("Aucune donnée")
    try:
        tout=pd.DataFrame(lire_tout_historique(1000))
        if not tout.empty:
            csv=tout.to_csv(index=False).encode("utf-8")
            ex4.download_button("📋 TOUT CSV",csv,f"historique_{datetime.now().strftime('%Y%m%d')}.csv","text/csv",use_container_width=True,type="primary")
    except Exception: pass

    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown("### 📜 Historique détaillé")
    tab_tout,tab_irr,tab_fert,tab_mal=st.tabs(["📋 Tout","💧 Irrigation","🌿 Fertilisation","🔬 Maladies"])

    with tab_tout:
        try:
            tout=lire_tout_historique(100)
            if tout:
                for l in tout:
                    mod=l.get("module","")
                    cl={"Irrigation":"hist-irr","Fertilisation":"hist-fert","Maladies":"hist-mal"}.get(mod,"")
                    ic={"Irrigation":"💧","Fertilisation":"🌿","Maladies":"🔬"}.get(mod,"📋")
                    conf=l.get("confiance",0)
                    clr_c="#27ae60" if conf>=70 else "#ff9800" if conf>=50 else "#e53935"
                    st.markdown(
                        f'<div class="hist-row {cl}"><div><b>{ic} {mod}</b> · {l.get("culture","?")} · {l.get("ville","?")}</div>'
                        f'<div style="color:#666">{l.get("date_analyse","")}</div>'
                        f'<div><b>{l.get("resultat","")}</b></div>'
                        f'<div style="color:{clr_c};font-weight:600">{conf:.1f}%</div></div>',unsafe_allow_html=True)
            else: st.info("Aucune analyse enregistrée")
        except Exception as e: st.error(f"Erreur: {e}")

    with tab_irr:
        try:
            rows=lire_historique_irrigation(100)
            if rows:
                df=pd.DataFrame(rows)
                cols=[c for c in ["date_analyse","ville","culture","stade","saison","type_sol","resultat","dose_mm","confiance"] if c in df.columns]
                st.dataframe(df[cols],use_container_width=True,hide_index=True)
            else: st.info("Aucune analyse irrigation")
        except Exception as e: st.error(f"Erreur: {e}")

    with tab_fert:
        try:
            rows=lire_historique_fertilisation(100)
            if rows:
                df=pd.DataFrame(rows)
                cols=[c for c in ["date_analyse","ville","culture","type_sol","zone","azote_n","phosphore_p","potassium_k","engrais_recommande","confiance"] if c in df.columns]
                st.dataframe(df[cols],use_container_width=True,hide_index=True)
            else: st.info("Aucune analyse fertilisation")
        except Exception as e: st.error(f"Erreur: {e}")

    with tab_mal:
        try:
            rows=lire_historique_maladies(100)
            if rows:
                df=pd.DataFrame(rows)
                cols=[c for c in ["date_analyse","ville","culture","methode","etat","confiance","ndvi","traitement"] if c in df.columns]
                st.dataframe(df[cols],use_container_width=True,hide_index=True)
            else: st.info("Aucune analyse maladies")
        except Exception as e: st.error(f"Erreur: {e}")

    st.markdown("<br>",unsafe_allow_html=True)
    with st.expander("⚠️ Zone danger — Vider l'historique"):
        st.warning("Cette action est irréversible !")
        vv1,vv2,vv3,vv4=st.columns(4)
        with vv1:
            if st.button("🗑️ Irrigation",use_container_width=True):
                vider_historique("irrigation"); st.success("✅ Vidé"); st.rerun()
        with vv2:
            if st.button("🗑️ Fertilisation",use_container_width=True):
                vider_historique("fertilisation"); st.success("✅ Vidé"); st.rerun()
        with vv3:
            if st.button("🗑️ Maladies",use_container_width=True):
                vider_historique("maladies"); st.success("✅ Vidé"); st.rerun()
        with vv4:
            if st.button("🗑️ TOUT",use_container_width=True,type="primary"):
                vider_historique("tout"); st.success("✅ Tout vidé"); st.rerun()

st.markdown("""<div class="footer">Base SQLite (historique.db) · Agro-IA Tchad · ENASTIC 2025/2026</div>""",unsafe_allow_html=True)
