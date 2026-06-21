# ══════════════════════════════════════════════════════════════════
# meteo_api.py — Utilitaire météo Open-Meteo (sans clé API)
# Partagé par les modules Irrigation et Détection des Maladies
# ══════════════════════════════════════════════════════════════════

import requests
import streamlit as st
from datetime import datetime, timedelta

# ── Coordonnées des 5 villes tchadiennes ─────────────────────────
VILLES_TCHAD = {
    "N'Djamena":  {"lat": 12.107, "lon": 15.044, "zone": "Sahélienne"},
    "Abéché":     {"lat": 13.829, "lon": 20.832, "zone": "Sahélienne"},
    "Sarh":       {"lat": 9.142,  "lon": 18.386, "zone": "Soudanienne"},
    "Moundou":    {"lat": 8.574,  "lon": 16.077, "zone": "Soudanienne"},
    "Bongor":     {"lat": 10.277, "lon": 15.372, "zone": "Soudanienne"},
}


@st.cache_data(ttl=1800)  # Cache 30 minutes
def get_meteo_actuelle(lat: float, lon: float) -> dict:
    """
    Récupère la météo actuelle + 7 jours de pluie cumulée
    via Open-Meteo (gratuit, sans clé API).

    Retourne un dict avec toutes les variables agronomiques.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":  lat,
        "longitude": lon,
        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
            "shortwave_radiation",
        ]),
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "et0_fao_evapotranspiration",
            "soil_moisture_0_to_7cm",
            "shortwave_radiation",
            "wind_speed_10m",
        ]),
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "et0_fao_evapotranspiration",
            "shortwave_radiation_sum",
            "wind_speed_10m_max",
        ]),
        "past_days":     14,   # 14 jours passés pour pluie_7j et pluie_14j
        "forecast_days": 1,
        "timezone":      "Africa/Ndjamena",
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        # ── Extraire les variables actuelles ─────────────────────
        cur = data.get("current", {})
        daily = data.get("daily", {})
        hourly = data.get("hourly", {})

        # Pluie cumulée sur 7 et 14 jours (données journalières passées)
        pluies_daily = daily.get("precipitation_sum", [])
        pluie_14j = sum(pluies_daily[-14:]) if len(pluies_daily) >= 14 else sum(pluies_daily)
        pluie_7j  = sum(pluies_daily[-7:])  if len(pluies_daily) >= 7  else sum(pluies_daily)

        # ETP du dernier jour disponible
        etp_daily = daily.get("et0_fao_evapotranspiration", [0])
        etp = etp_daily[-1] if etp_daily else 5.0

        # Rayonnement solaire (MJ/m²/jour)
        rad_daily = daily.get("shortwave_radiation_sum", [20])
        rayonnement = rad_daily[-1] if rad_daily else 20.0

        # Température max du jour
        t_max_daily = daily.get("temperature_2m_max", [])
        temperature_max = t_max_daily[-1] if t_max_daily else cur.get("temperature_2m", 35) + 7

        # Humidité du sol (couche 0-7cm, valeur horaire la plus récente)
        soil_m = hourly.get("soil_moisture_0_to_7cm", [])
        humidite_sol_frac = soil_m[-1] if soil_m else 0.2
        humidite_sol = round(humidite_sol_frac * 100, 1)  # fraction → %

        return {
            "ok":                True,
            "temperature_moy":   round(cur.get("temperature_2m", 35.0), 1),
            "temperature_max":   round(temperature_max, 1),
            "humidite_air":      round(cur.get("relative_humidity_2m", 30.0), 1),
            "pluie_heure":       round(cur.get("precipitation", 0.0), 1),
            "pluie_7j":          round(pluie_7j, 1),
            "pluie_14j":         round(pluie_14j, 1),
            "vent_moy":          round(cur.get("wind_speed_10m", 3.0) / 3.6, 1),  # km/h → m/s
            "rayonnement":       round(rayonnement, 1),
            "etp":               round(etp, 2),
            "humidite_sol":      humidite_sol,
            "heure_maj":         datetime.now().strftime("%H:%M"),
        }

    except requests.exceptions.ConnectionError:
        return {"ok": False, "erreur": "Connexion impossible — vérifiez internet"}
    except requests.exceptions.Timeout:
        return {"ok": False, "erreur": "Délai dépassé (timeout 10s)"}
    except requests.exceptions.HTTPError as e:
        return {"ok": False, "erreur": f"Erreur HTTP : {e}"}
    except Exception as e:
        return {"ok": False, "erreur": f"Erreur inattendue : {str(e)}"}


def afficher_meteo_widget(meteo: dict, ville: str) -> None:
    """Affiche un widget compact de la météo actuelle."""
    if not meteo.get("ok"):
        st.warning(f"⚠️ Météo indisponible : {meteo.get('erreur', 'Erreur inconnue')}")
        return

    st.success(f"🛰️ Météo en temps réel — **{ville}** (Open-Meteo) · Mis à jour à {meteo['heure_maj']}")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🌡️ Température",   f"{meteo['temperature_moy']} °C")
    c2.metric("💧 Humidité air",   f"{meteo['humidite_air']} %")
    c3.metric("🌧️ Pluie 7j",      f"{meteo['pluie_7j']} mm")
    c4.metric("💨 Vent",           f"{meteo['vent_moy']} m/s")
    c5.metric("☀️ ETP",            f"{meteo['etp']} mm/j")
