# 🌾 Agro-IA Tchad — Guide Ubuntu

## Structure du projet

```
agro_ia_app/
├── app.py                    ← Page d'accueil
├── database.py               ← Gestion SQLite
├── meteo_api.py              ← API Open-Meteo
├── styles.py                 ← CSS global
├── requirements.txt          ← Dépendances Python
├── install_ubuntu.sh         ← Script d'installation
├── historique.db             ← Base SQLite (créée automatiquement)
├── .streamlit/
│   └── config.toml
├── models/
│   ├── model_irrigation.pkl
│   ├── scaler_irrigation.pkl
│   ├── model_fertilisation.pkl
│   ├── scaler_fertilisation.pkl
│   ├── label_encoder_engrais.pkl
│   ├── label_encoder_culture.pkl
│   ├── label_encoder_sol.pkl
│   ├── model_maladie_cnn.h5
│   └── config_maladies.json
└── pages/
    ├── 1_Irrigation.py
    ├── 2_Fertilisation.py
    ├── 3_Detection_Maladies.py
    └── 4_Historique.py       ← NOUVEAU — Historique SQLite
```

## Installation sur Ubuntu

```bash
# 1. Cloner le projet
git clone https://github.com/tourabiissakhissein33-dev/PFE_Agriculture_IA.git
cd PFE_Agriculture_IA

# 2. Lancer le script d'installation
chmod +x install_ubuntu.sh
./install_ubuntu.sh

# 3. Activer le venv et lancer
source .venv/bin/activate
streamlit run app.py
```

## Installation manuelle

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv -y

python3.11 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

streamlit run app.py
```

## Nouveautés — Historique SQLite

- Toutes les analyses sont sauvegardées automatiquement
- Page dédiée `📋 Historique` avec tableau de bord
- Export CSV par module (Irrigation / Fertilisation / Maladies)
- Statistiques : culture + analysée, zone à risque, taux

## Accès à l'application

```
http://localhost:8501

https://agro-ia-tchad.streamlit.app/
```

## PFE ENASTIC 2025/2026
- **Étudiant :** TOURABI ISSAK HISSEIN
- **Encadreur :** Dr. MOUAZ MIKAIL
