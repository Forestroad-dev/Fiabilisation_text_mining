import pandas as pd
import re

def validate_excel(file_path, output_path):

    df = pd.read_excel(file_path)

    invalid_rows = []

    valid_domains = ["gmail.com", "hotmail.fr","hotmail.com", "yahoo.com", "yahoo.fr", "gmail.fr", "outlook.com", "icloud.com", "icloud.fr", "ucad.edu.sn","outlook.fr","cofinacorp.com","live.fr","hotmail.it","gainde2000.sn"]

    required_packs = [
        "COMPTE COURANT STAFF", "EPARGNE LIBRE PARTICULIER", "PACK NDANANE","PACK DALAL" ,"PACK CLASSIC" , "PACK PRIVILEGE" ,
        "PACK NJEGUEMAR'LA", "PACK SOXNA'LA" ,"EPARGNE LIBRE STAFF","PACK TERANGA","EPARGNE YAKHANAAL", "EPARGNE LIBRE DIASPORA CSF"
    ]

    for idx, row in df.iterrows():
        Matricule_Client = row.get('Matricule Client', 'Inconnu')
        Nom_Client       = row.get('Nom Client',       'Inconnu')
        Date_Ouverture_Compte       = row.get('Date Ouverture Compte',       'Inconnu')
        Agence           = row.get('Agence',           'Inconnu')
        Num_compte       = row.get('N° Compte',        'Inconnu')
        CC               = row.get('CC',               'Inconnu')
        
        errors = {
            "Matricule Client": Matricule_Client,
            "Nom Client": Nom_Client,
            "Date Ouverture Compte": Date_Ouverture_Compte ,
            "Agence":Agence,
            "N° Compte":Num_compte,
            "CC":CC,
            
            "Format du Numéro de Téléphone Invalide": "",
            "Domaine ou Format de l'Email Invalide": "",
            "Sexe ou Genre Incorrect ou Manquant pour Entreprise": "",
            "Représentant Légal Manquant": ""
        }
        country_phone_rules = {
            'Burkina Faso': {'code': '226', 'length': 8},
            'Côte d\'Ivoire': {'code': '225', 'length': 10},
            'Guinée': {'code': '224', 'length': 9},
            'Mali': {'code': '223', 'length': 8},
            'Sénégal': {'code': '221', 'length': 9},
            'Togo': {'code': '228', 'length': 8},
            'Congo': {'code': '242', 'length': 9},
            'Gabon': {'code': '241', 'length': 8},
            'France': {'code': '33', 'length': 9},
            'Maroc': {'code': '212', 'length': 9},
            'Espagne': {'code': '34', 'length': 9},
            'Belgique': {'code': '32', 'length': 9}
        }


        phone_raw = row.get('Telephone Client', '')

        phone = re.sub(r'\D', '', str(phone_raw)) if not pd.isna(phone_raw) else ""
        
        valid_format = False

        for country, rules in country_phone_rules.items():
            valid_number_without_code = len(phone) == rules['length']
            valid_number_with_code = (
                phone.startswith(rules['code']) and len(phone) == rules['length'] + len(rules['code']) or
                phone.startswith('00' + rules['code']) and len(phone) == rules['length'] + len(rules['code']) + 2 or
                phone.startswith('+' + rules['code']) and len(phone) == rules['length'] + len(rules['code']) + 1
            )
            if valid_number_without_code or valid_number_with_code:
                valid_format = True
                break
        if not valid_format:
            errors["Format du Numéro de Téléphone Invalide"] = (
                "Numéro de téléphone manquant ou format invalide (doit correspondre au format d'un des pays autorisés)"
            )

        valid_extensions = r'(com|org|net|edu|gov|mil|int|info|biz|fr|sn|us|uk|ca|de|es|cn|in|br|jp|au|online|tech|site|store|app|io|xyz|club|blog|bank|law|pharma|media|travel|shop|it)$'

        email = str(row.get('Email Client', '')).strip() if not pd.isna(row.get('Email Client', '')) else ""
        
        if email:
            domain = email.split('@')[-1] if "@" in email else None
            if domain not in valid_domains:
                if not re.match(r'^[\w\.-]+@[\w\.-]+\.' + valid_extensions, email):
                    errors["Domaine ou Format de l'Email Invalide"] = "Format ou domaine de l'email invalide"
            elif not re.match(r'^[\w\.-]+@[\w\.-]+\.' + valid_extensions, email):
                errors["Domaine ou Format de l'Email Invalide"] = "Format de l'email invalide"

        sexe = str(row.get('SEXE', '')).upper() if not pd.isna(row.get('SEXE', '')) else ""
        genre_entreprise = str(row.get('Genre Pour Entreprise', '')).upper() if not pd.isna(row.get('Genre Pour Entreprise', '')) else ""
        
        sexe_normalized = ""
        genre_entreprise_normalized = ""

        if sexe in ["F", "FEMININ"]:
            sexe_normalized = "F"
        elif sexe in ["M", "MASCULIN"]:
            sexe_normalized = "M"
        if genre_entreprise in ["F", "FEMININ"]:
            genre_entreprise_normalized = "F"
        elif genre_entreprise in ["M", "MASCULIN"]:
            genre_entreprise_normalized = "M"

        if not sexe_normalized and not genre_entreprise_normalized:
            errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = "Sexe et Genre manquants"
        elif sexe_normalized and genre_entreprise_normalized and sexe_normalized != genre_entreprise_normalized:
            errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = "Sexe et Genre ne correspondent pas"
        elif not sexe_normalized and genre_entreprise_normalized not in ["F", "M"]:
            errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = "Sexe ou Genre incorrect ou manquant"

        pack_type = str(row.get('Type de Pack', '')).upper() if not pd.isna(row.get('Type de Pack', '')) else ""
        representant_legal = str(row.get('Representant Legal', '')).strip() if not pd.isna(row.get('Representant Legal', '')) else ""
        genre_entreprise = str(row.get('Genre Pour Entreprise', '')).upper() if not pd.isna(row.get('Genre Pour Entreprise', '')) else ""

        if pack_type not in required_packs:
            if not representant_legal:
                errors["Représentant Légal Manquant"] = "Représentant Légal manquant"
            if not genre_entreprise:
                errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = "Le genre de l'entreprise est requis"
        if any(errors[column] for column in errors if column not in ["Matricule Client", "Nom Client", "Date Ouverture Compte", "Agence", "N° Compte", "CC"]):
            invalid_rows.append(errors)

    if invalid_rows:
        invalid_df = pd.DataFrame(invalid_rows)
        invalid_df.to_excel(output_path, index=False)
        return invalid_df
    else:
        return pd.DataFrame()  # Retourner un DataFrame vide
