#!/usr/bin/env python
# coding: utf-8

# In[7]:


# %pip install openpyxl
# %pip install pyinstaller
# %pip install --upgrade pip
# !pyinstaller --onefile --windowed fiabilisation.ipynb


# In[8]:


import pandas as pd
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

def validate_excel(file_path, output_path):
    # Charger le fichier Excel
    df = pd.read_excel(file_path)

    # Liste pour stocker les lignes invalides avec les différentes colonnes pour chaque condition
    invalid_rows = []

    # Liste des domaines de messagerie valides
    valid_domains = ["gmail.com", "hotmail.fr","hotmail.com", "yahoo.com", "yahoo.fr", "gmail.fr", "outlook.com", "icloud.com", "icloud.fr", "ucad.edu.sn","outlook.fr","cofinacorp.com","live.fr","hotmail.it","gainde2000.sn"]

    # Types de PACK nécessitant un représentant légal et un genre
    required_packs = [
        "COMPTE COURANT STAFF", "EPARGNE LIBRE PARTICULIER", "PACK NDANANE",
        "PACK NJEGUEMAR'LA", "PACK SOXNA'LA" ,"EPARGNE LIBRE STAFF","PACK TERANGA","EPARGNE YAKHANAAL", "EPARGNE LIBRE DIASPORA CSF"
    ]

    for idx, row in df.iterrows():
        # Récupération des valeurs de la ligne
        Matricule_Client = row.get('Matricule Client', 'Inconnu')
        Nom_Client = row.get('Nom Client', 'Inconnu')
        errors = {
            "Matricule Client": Matricule_Client,
            # "Nom Client": Nom_Client,
            "Format du Numéro de Téléphone Invalide": "",
            "Domaine ou Format de l'Email Invalide": "",
            "Sexe ou Genre Incorrect ou Manquant pour Entreprise": "",
            "Représentant Légal Manquant pour le Pack Requis": ""
        }

        # Dictionnaire des pays avec leurs codes d'indicatif et longueurs de numéros de téléphone
        country_phone_rules = {
            'Burkina Faso': {'code': '226', 'length': 8},
            'Côte d\'Ivoire': {'code': '225', 'length': 10},
            'Guinée': {'code': '224', 'length': 9},
            'Mali': {'code': '223', 'length': 8},
            'Sénégal': {'code': '221', 'length': 9},
            'Togo': {'code': '228', 'length': 8},
            'Congo': {'code': '242', 'length': 9},  # Assumer Congo-Brazzaville ici
            'Gabon': {'code': '241', 'length': 8},
            'France': {'code': '33', 'length': 9},
            'Maroc': {'code': '212', 'length': 9}
        }

        # Valeur brute du numéro de téléphone
        phone_raw = row.get('Telephone Client', '')  # Extrait le numéro brut

        # Nettoyage du numéro en supprimant les caractères non numériques
        phone = re.sub(r'\D', '', str(phone_raw)) if not pd.isna(phone_raw) else ""

        # Debugging: Afficher la valeur brute et nettoyée du téléphone pour ce Matricule
        if Matricule_Client == 17452911:
            print(f"Matricule: {Matricule_Client}, Téléphone (brut): '{phone_raw}', Téléphone (nettoyé): '{phone}'")

        # Initialisation du statut de validation
        valid_format = False

        # Parcourir chaque règle de pays pour vérifier le format
        for country, rules in country_phone_rules.items():
            # Vérification sans indicatif
            valid_number_without_code = len(phone) == rules['length']
            
            # Vérification avec indicatif (+, 00 ou sans)
            valid_number_with_code = (
                phone.startswith(rules['code']) and len(phone) == rules['length'] + len(rules['code']) or
                phone.startswith('00' + rules['code']) and len(phone) == rules['length'] + len(rules['code']) + 2 or
                phone.startswith('+' + rules['code']) and len(phone) == rules['length'] + len(rules['code']) + 1
            )
            
            # Si le format est valide pour l'un des pays, arrêter la vérification
            if valid_number_without_code or valid_number_with_code:
                valid_format = True
                break

        # Ajout d'une erreur si le format est invalide pour tous les pays
        if not valid_format:
            errors["Format du Numéro de Téléphone Invalide"] = (
                "Numéro de téléphone manquant ou format invalide (doit correspondre au format d'un des pays autorisés)"
            )

        # Condition 2: Validation de l'email si spécifiée (email optionnel)
        
        # Liste des extensions de domaine acceptées
        valid_extensions = r'(com|org|net|edu|gov|mil|int|info|biz|fr|sn|us|uk|ca|de|es|cn|in|br|jp|au|online|tech|site|store|app|io|xyz|club|blog|bank|law|pharma|media|travel|shop|it)$'

        email = str(row.get('Email Client', '')).strip() if not pd.isna(row.get('Email Client', '')) else ""
        
        if email:  # Vérifie seulement si l'email est renseigné
            domain = email.split('@')[-1] if "@" in email else None
        
        # Vérifier si le domaine est dans la liste des domaines spécifiques
            if domain not in valid_domains:
                # Si le domaine n'est pas dans valid_domains, vérifier uniquement l'extension
                if not re.match(r'^[\w\.-]+@[\w\.-]+\.' + valid_extensions, email):
                    errors["Domaine ou Format de l'Email Invalide"] = "Format ou domaine de l'email invalide"
                # Si l'extension est valide mais le domaine est inconnu, aucune erreur n'est ajoutée.
            elif not re.match(r'^[\w\.-]+@[\w\.-]+\.' + valid_extensions, email):
                # Si le domaine est correct mais le format échoue
                errors["Domaine ou Format de l'Email Invalide"] = "Format de l'email invalide"

        # Condition 3: Vérification du sexe et du genre pour entreprise
        sexe = str(row.get('SEXE', '')).upper() if not pd.isna(row.get('SEXE', '')) else ""
        genre_entreprise = str(row.get('Genre Pour Entreprise', '')).upper() if not pd.isna(row.get('Genre Pour Entreprise', '')) else ""
        
        # Normalisation des valeurs de sexe et de genre_entreprise pour comparer équitablement
        
        sexe_normalized = ""
        genre_entreprise_normalized = ""

        # Normaliser les valeurs de sexe
        if sexe in ["F", "FEMININ"]:
            sexe_normalized = "F"
        elif sexe in ["M", "MASCULIN"]:
            sexe_normalized = "M"

        # Normaliser les valeurs de genre_entreprise
        if genre_entreprise in ["F", "FEMININ"]:
            genre_entreprise_normalized = "F"
        elif genre_entreprise in ["M", "MASCULIN"]:
            genre_entreprise_normalized = "M"

        # Conditions après normalisation
        if not sexe_normalized and not genre_entreprise_normalized:
            errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = "Sexe et Genre manquants"
        elif sexe_normalized and genre_entreprise_normalized and sexe_normalized != genre_entreprise_normalized:
            errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = "Sexe et Genre ne correspondent pas"
        elif not sexe_normalized and genre_entreprise_normalized not in ["F", "M"]:
            errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = "Sexe ou Genre incorrect ou manquant"


        # Condition 4: Vérification du représentant légal pour certains types de PACK
        pack_type = str(row.get('Type de Pack', '')).upper() if not pd.isna(row.get('Type de Pack', '')) else ""
        representant_legal = str(row.get('Representant Legal', '')).strip() if not pd.isna(row.get('Representant Legal', '')) else ""
        genre_entreprise = str(row.get('Genre Pour Entreprise', '')).upper() if not pd.isna(row.get('Genre Pour Entreprise', '')) else ""

        # Vérifier si le type de pack n'est pas dans les packs qui nécessitent un représentant légal
        if pack_type not in required_packs:
            # Si le représentant légal ou le genre est manquant, ajouter une erreur
            if not representant_legal:
                errors["Représentant Légal Manquant pour le Pack Requis"] = "Représentant Légal manquant"
            if not genre_entreprise:
                errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = "Le genre de l'entreprise est requis"

        # Ajouter les erreurs pour la ligne si au moins une condition est invalide
        if any(errors[column] for column in errors if column != "Matricule Client"):
            invalid_rows.append(errors)


    # Créer un DataFrame des lignes invalides avec les colonnes pour chaque condition
    if invalid_rows:
        invalid_df = pd.DataFrame(invalid_rows)
        invalid_df.to_excel(output_path, index=False)  # Exporter en fichier Excel
        return invalid_df
    else:
        return "Toutes les lignes répondent aux critères de validation."

# # Utilisation
# file_path = "C:/Users/djibril.marwan/Documents/Comptes Ouverts entre Mai et Septembre 2024 COFSN.xlsx"
# output_path = "C:/Users/djibril.marwan/Documents/invalid_rows.xlsx"
# invalid_data = validate_excel(file_path, output_path)

# # Affiche le nombre de lignes avec erreurs et le fichier Excel généré
# if isinstance(invalid_data, pd.DataFrame):
#     print(f"Nombre de lignes avec erreurs: {invalid_data.shape[0]}")
#     print("Le fichier Excel contenant les lignes invalides par condition a été généré.")
# else:
#     print(invalid_data)  # Affiche "Toutes les lignes répondent aux critères de validation" si tout est correct

# print(invalid_data)


# In[ ]:


