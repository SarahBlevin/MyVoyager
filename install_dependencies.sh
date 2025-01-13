#!/bin/bash

# #To Start
# #chmod +x install_dependencies.sh
# #./install_dependencies.sh

# # Arrêter le script en cas d'erreur
# set -e

# # Définir l'environnement virtuel
# VENV_DIR="venv"

# # Vérifier si Python est installé
# if ! command -v python3 &> /dev/null; then
#     echo "Erreur : Python 3 n'est pas installé. Veuillez l'installer avant de continuer."
#     exit 1
# fi

# # Vérifier si pip est installé
# if ! command -v pip &> /dev/null; then
#     echo "Erreur : pip n'est pas installé. Veuillez l'installer avant de continuer."
#     exit 1
# fi

# # Créer un environnement virtuel si nécessaire
# if [ ! -d "$VENV_DIR" ]; then
#     echo "Création de l'environnement virtuel dans $VENV_DIR..."
#     python3 -m venv "$VENV_DIR"
# else
#     echo "Environnement virtuel déjà existant dans $VENV_DIR."
# fi

# # Activer l'environnement virtuel
# source "$VENV_DIR/bin/activate"

# Mettre à jour pip
echo "Mise à jour de pip..."
pip install --upgrade pip

# Installer les dépendances
if [ -f "requirements.txt" ]; then
    echo "Installation des dépendances à partir de requirements.txt..."
    pip install -r requirements.txt
else
    echo "Erreur : fichier requirements.txt introuvable."
    deactivate
    exit 1
fi

# Indiquer la fin de l'installation
echo "Toutes les dépendances ont été installées avec succès."

# Désactiver l'environnement virtuel
deactivate
