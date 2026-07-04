import sqlite3, os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),"historique.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialiser_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS irrigation(
        id INTEGER PRIMARY KEY AUTOINCREMENT, date_analyse TEXT,
        ville TEXT, culture TEXT, stade TEXT, zone TEXT, saison TEXT,
        type_sol TEXT, temperature_moy REAL, humidite_air REAL,
        pluie_7j REAL, humidite_sol REAL, etp REAL,
        resultat TEXT, dose_mm REAL, confiance REAL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS fertilisation(
        id INTEGER PRIMARY KEY AUTOINCREMENT, date_analyse TEXT,
        ville TEXT, culture TEXT, type_sol TEXT, zone TEXT,
        azote_n REAL, phosphore_p REAL, potassium_k REAL, ph_sol REAL,
        temperature REAL, humidite_air REAL, pluie REAL,
        engrais_recommande TEXT, confiance REAL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS maladies(
        id INTEGER PRIMARY KEY AUTOINCREMENT, date_analyse TEXT,
        ville TEXT, culture TEXT, methode TEXT, resultat TEXT,
        etat TEXT, confiance REAL, ndvi REAL, temperature REAL,
        humidite_air REAL, pluie_7j REAL, traitement TEXT)""")
    conn.commit(); conn.close()

def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def sauvegarder_irrigation(ville,culture,stade,zone,saison,type_sol,
    temperature_moy,humidite_air,pluie_7j,humidite_sol,etp,resultat,dose_mm,confiance):
    conn = get_conn()
    conn.execute("""INSERT INTO irrigation(date_analyse,ville,culture,stade,zone,
        saison,type_sol,temperature_moy,humidite_air,pluie_7j,humidite_sol,etp,
        resultat,dose_mm,confiance) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (_now(),ville,culture,stade,zone,saison,type_sol,temperature_moy,
         humidite_air,pluie_7j,humidite_sol,etp,resultat,dose_mm,confiance))
    conn.commit(); conn.close()

def sauvegarder_fertilisation(ville,culture,type_sol,zone,azote_n,phosphore_p,
    potassium_k,ph_sol,temperature,humidite_air,pluie,engrais_recommande,confiance):
    conn = get_conn()
    conn.execute("""INSERT INTO fertilisation(date_analyse,ville,culture,type_sol,zone,
        azote_n,phosphore_p,potassium_k,ph_sol,temperature,humidite_air,pluie,
        engrais_recommande,confiance) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (_now(),ville,culture,type_sol,zone,azote_n,phosphore_p,potassium_k,
         ph_sol,temperature,humidite_air,pluie,engrais_recommande,confiance))
    conn.commit(); conn.close()

def sauvegarder_maladie(ville,culture,methode,resultat,etat,confiance,
    ndvi=None,temperature=None,humidite_air=None,pluie_7j=None,traitement=None):
    conn = get_conn()
    conn.execute("""INSERT INTO maladies(date_analyse,ville,culture,methode,
        resultat,etat,confiance,ndvi,temperature,humidite_air,pluie_7j,traitement)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (_now(),ville,culture,methode,resultat,etat,confiance,
         ndvi,temperature,humidite_air,pluie_7j,traitement))
    conn.commit(); conn.close()

def lire_historique_irrigation(limit=100):
    conn=get_conn(); rows=conn.execute("SELECT * FROM irrigation ORDER BY id DESC LIMIT ?",
        (limit,)).fetchall(); conn.close(); return [dict(r) for r in rows]

def lire_historique_fertilisation(limit=100):
    conn=get_conn(); rows=conn.execute("SELECT * FROM fertilisation ORDER BY id DESC LIMIT ?",
        (limit,)).fetchall(); conn.close(); return [dict(r) for r in rows]

def lire_historique_maladies(limit=100):
    conn=get_conn(); rows=conn.execute("SELECT * FROM maladies ORDER BY id DESC LIMIT ?",
        (limit,)).fetchall(); conn.close(); return [dict(r) for r in rows]

def lire_tout_historique(limit=100):
    conn=get_conn()
    irr  = conn.execute("SELECT date_analyse,'Irrigation' as module,culture,ville,resultat,confiance FROM irrigation ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    fert = conn.execute("SELECT date_analyse,'Fertilisation' as module,culture,ville,engrais_recommande as resultat,confiance FROM fertilisation ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    mal  = conn.execute("SELECT date_analyse,'Maladies' as module,culture,ville,resultat,confiance FROM maladies ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    conn.close()
    tout = [dict(r) for r in irr+fert+mal]
    tout.sort(key=lambda x:x["date_analyse"],reverse=True)
    return tout[:limit]

def statistiques():
    conn=get_conn()
    n_irr  = conn.execute("SELECT COUNT(*) FROM irrigation").fetchone()[0]
    n_fert = conn.execute("SELECT COUNT(*) FROM fertilisation").fetchone()[0]
    n_mal  = conn.execute("SELECT COUNT(*) FROM maladies").fetchone()[0]
    top = conn.execute("""SELECT culture,COUNT(*) as n FROM(
        SELECT culture FROM irrigation UNION ALL SELECT culture FROM fertilisation
        UNION ALL SELECT culture FROM maladies) GROUP BY culture ORDER BY n DESC LIMIT 1""").fetchone()
    zr = conn.execute("SELECT ville,COUNT(*) as n FROM maladies WHERE etat='Malade' GROUP BY ville ORDER BY n DESC LIMIT 1").fetchone()
    irr_oui = conn.execute("SELECT COUNT(*) FROM irrigation WHERE resultat='OUI'").fetchone()[0]
    mal_det = conn.execute("SELECT COUNT(*) FROM maladies WHERE etat='Malade'").fetchone()[0]
    conn.close()
    return {"n_irrigation":n_irr,"n_fertilisation":n_fert,"n_maladies":n_mal,
            "total":n_irr+n_fert+n_mal,"top_culture":top[0] if top else "—",
            "zone_risque":zr[0] if zr else "—",
            "taux_irrigation":round(irr_oui/n_irr*100,1) if n_irr>0 else 0,
            "taux_maladie":round(mal_det/n_mal*100,1) if n_mal>0 else 0}

def vider_historique(module="tout"):
    conn=get_conn()
    if module in("tout","irrigation"):   conn.execute("DELETE FROM irrigation")
    if module in("tout","fertilisation"):conn.execute("DELETE FROM fertilisation")
    if module in("tout","maladies"):     conn.execute("DELETE FROM maladies")
    conn.commit(); conn.close()

initialiser_db()
