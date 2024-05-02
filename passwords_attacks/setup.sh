#!/bin/bash

# Définir le dossier de destination
destination_folder="passwords_attacks"

# Créer le dossier s'il n'existe pas
mkdir -p "$destination_folder"

# Télécharger rockyou.txt depuis GitHub
wget -P "$destination_folder" https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt

echo "Téléchargement terminé. Le fichier rockyou.txt se trouve dans : $destination_folder"