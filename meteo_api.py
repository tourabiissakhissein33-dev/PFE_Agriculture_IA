import requests, streamlit as st
from datetime import datetime

VILLES_TCHAD = {
    "N'Djamena": {"lat":12.107,"lon":15.044,"zone":"Sahélienne"},
    "Abéché":    {"lat":13.829,"lon":20.832,"zone":"Sahélienne"},
    "Sarh":      {"lat":9.142, "lon":18.386,"zone":"Soudanienne"},
    "Moundou":   {"lat":8.574, "lon":16.077,"zone":"Soudanienne"},
    "Bongor":    {"lat":10.277,"lon":15.372,"zone":"Soudanienne"},
}

@st.cache_data(ttl=1800)
def get_meteo_actuelle(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":lat,"longitude":lon,
        "current":"temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "hourly":"temperature_2m,relative_humidity_2m,precipitation,et0_fao_evapotranspiration,soil_moisture_0_to_7cm,shortwave_radiation",
        "daily":"temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration,shortwave_radiation_sum",
        "past_days":14,"forecast_days":1,"timezone":"Africa/Ndjamena",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        d = r.json()
        cur   = d.get("current",{})
        daily = d.get("daily",{})
        hourly= d.get("hourly",{})
        pluies = daily.get("precipitation_sum",[])
        etp_d  = daily.get("et0_fao_evapotranspiration",[5.0])
        rad_d  = daily.get("shortwave_radiation_sum",[20.0])
        t_max  = daily.get("temperature_2m_max",[])
        soil   = hourly.get("soil_moisture_0_to_7cm",[])
        return {
            "ok":True,
            "temperature_moy": round(cur.get("temperature_2m",35.0),1),
            "temperature_max": round(t_max[-1] if t_max else cur.get("temperature_2m",35)+7,1),
            "humidite_air":    round(cur.get("relative_humidity_2m",30.0),1),
            "pluie_heure":     round(cur.get("precipitation",0.0),1),
            "pluie_7j":        round(sum(pluies[-7:]) if len(pluies)>=7 else sum(pluies),1),
            "pluie_14j":       round(sum(pluies[-14:]) if len(pluies)>=14 else sum(pluies),1),
            "vent_moy":        round(cur.get("wind_speed_10m",3.0)/3.6,1),
            "rayonnement":     round(rad_d[-1] if rad_d else 20.0,1),
            "etp":             round(etp_d[-1] if etp_d else 5.0,2),
            "humidite_sol":    round((soil[-1] if soil else 0.2)*100,1),
            "heure_maj":       datetime.now().strftime("%H:%M"),
        }
    except Exception as e:
        return {"ok":False,"erreur":str(e)}
