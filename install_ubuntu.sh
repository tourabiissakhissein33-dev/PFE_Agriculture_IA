#!/bin/bash
# ══════════════════════════════════════════════════════════════════
# install_ubuntu.sh — Installation sur Ubuntu
# Agro-IA Tchad — PFE ENASTIC 2025/2026
# ══════════════════════════════════════════════════════════════════

echo "🚀 Installation Agro-IA Tchad sur Ubuntu"
echo "========================================="

# 1. Mettre à jour le système
echo "📦 Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

# 2. Installer Python 3.11
echo "🐍 Installation Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3.11-pip python3-pip

# 3. Vérifier Python
python3.11 --version

# 4. Créer l'environnement virtuel
echo "🔧 Création de l'environnement virtuel..."
python3.11 -m venv .venv

# 5. Activer le venv
source .venv/bin/activate

# 6. Mettre à jour pip
pip install --upgrade pip

# 7. Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -r requirements.txt

# 8. Vérifier les installations
echo ""
echo "✅ Vérification des installations :"
python -c "import streamlit; print('  Streamlit :', streamlit.__version__)"
python -c "import tensorflow; print('  TensorFlow:', tensorflow.__version__)"
python -c "import sklearn; print('  Sklearn   :', sklearn.__version__)"
python -c "import xgboost; print('  XGBoost   :', xgboost.__version__)"
python -c "import sqlite3; print('  SQLite3   :', sqlite3.version)"

echo ""
echo "🎉 Installation terminée !"
echo ""
echo "Pour lancer l'application :"
echo "  source .venv/bin/activate"
echo "  streamlit run app.py"
