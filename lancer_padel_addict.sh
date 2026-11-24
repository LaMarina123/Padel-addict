#!/bin/bash
cd "$(dirname "$0")"
echo "Installation des dépendances si nécessaire..."
pip install -r requirements.txt
echo "Lancement de Padel Addict..."
streamlit run app.py
