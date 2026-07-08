# ndvi_sentinel.py — NDVI automatique Sentinel-2 + caméra
# Agro-IA Tchad — PFE ENASTIC 2025/2026

import requests
import numpy as np
import streamlit as st
from datetime import date, timedelta

# ── CONFIG SENTINEL HUB ───────────────────────────────────────────
# Compte gratuit sur : https://shapps.dataspace.copernicus.eu/
SENTINEL_CLIENT_ID     = "VOTRE_CLIENT_ID"
SENTINEL_CLIENT_SECRET = "VOTRE_CLIENT_SECRET"
TOKEN_URL   = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"


def obtenir_token():
    try:
        r = requests.post(TOKEN_URL, data={
            "grant_type":    "client_credentials",
            "client_id":     SENTINEL_CLIENT_ID,
            "client_secret": SENTINEL_CLIENT_SECRET,
        }, timeout=10)
        r.raise_for_status()
        return r.json().get("access_token")
    except Exception:
        return None


@st.cache_data(ttl=86400)
def ndvi_sentinel2(lat: float, lon: float, rayon_km: float = 1.0):
    """NDVI automatique depuis Sentinel-2 (ESA, gratuit)."""
    token = obtenir_token()
    if not token:
        return {"ok": False, "erreur": "Vérifiez CLIENT_ID et CLIENT_SECRET"}

    delta   = rayon_km / 111.0
    bbox    = [lon-delta, lat-delta, lon+delta, lat+delta]
    fin     = date.today()
    debut   = fin - timedelta(days=30)

    evalscript = """
    //VERSION=3
    function setup(){return{input:[{bands:["B04","B08","SCL"]}],
        output:{bands:1,sampleType:"FLOAT32"}}}
    function evaluatePixel(s){
        if(s.SCL>6) return [NaN];
        return [(s.B08-s.B04)/(s.B08+s.B04)];
    }"""

    payload = {
        "input": {
            "bounds": {"bbox": bbox,
                "properties":{"crs":"http://www.opengis.net/def/crs/EPSG/0/4326"}},
            "data": [{"type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {"from":f"{debut}T00:00:00Z","to":f"{fin}T23:59:59Z"},
                    "maxCloudCoverage": 30,
                    "mosaickingOrder": "leastCC"
                }}]
        },
        "output": {"width":64,"height":64,
            "responses":[{"identifier":"default","format":{"type":"image/tiff"}}]},
        "evalscript": evalscript
    }

    try:
        r = requests.post(PROCESS_URL,
            headers={"Authorization":f"Bearer {token}",
                     "Content-Type":"application/json","Accept":"image/tiff"},
            json=payload, timeout=30)
        r.raise_for_status()

        import io, rasterio
        with rasterio.open(io.BytesIO(r.content)) as src:
            arr = src.read(1).astype(float)
            arr[(arr<-1)|(arr>1)] = np.nan
            return {"ok":True,
                    "ndvi_moyen": round(float(np.nanmean(arr)),3),
                    "ndvi_min":   round(float(np.nanmin(arr)),3),
                    "ndvi_max":   round(float(np.nanmax(arr)),3),
                    "date":       str(fin),
                    "source":     "Sentinel-2 L2A (ESA)"}
    except ImportError:
        return {"ok":False,"erreur":"pip install rasterio"}
    except Exception as e:
        return {"ok":False,"erreur":str(e)}


def ndvi_camera(image_pil):
    """NDVI approximatif depuis photo smartphone (VARI)."""
    img = image_pil.convert("RGB").resize((224,224))
    arr = np.array(img, dtype=np.float32) / 255.0
    R,G,B = arr[:,:,0], arr[:,:,1], arr[:,:,2]

    # VARI = (G-R)/(G+R-B)
    denom = G + R - B
    denom[np.abs(denom)<0.001] = 0.001
    vari = np.clip((G-R)/denom, -1, 1)
    vari_moy = float(np.mean(vari))

    # VARI → NDVI estimé (corrélation empirique)
    ndvi = round(0.18 + 0.73 * vari_moy, 3)
    ndvi = max(-1.0, min(1.0, ndvi))

    if ndvi > 0.5:   etat="Saine"
    elif ndvi > 0.3: etat="Stress"
    else:            etat="Malade"

    return {"ndvi_estime":ndvi,"vari":round(vari_moy,3),
            "etat":etat,"source":"Caméra (VARI→NDVI estimation)"}
