import pandas as pd
import re
import tldextract
import validators
import phonenumbers

# def validate_excel(file_path, output_path):

#     df = pd.read_excel(file_path)

#     invalid_rows = []

#     valid_domains = ["gmail.com", "hotmail.fr","hotmail.com", "yahoo.com", "yahoo.fr", "gmail.fr", "outlook.com", "icloud.com", "icloud.fr", "ucad.edu.sn","outlook.fr","cofinacorp.com","live.fr","hotmail.it","gainde2000.sn"]

#     required_packs = [
#         "COMPTE COURANT STAFF", "EPARGNE LIBRE PARTICULIER", "PACK NDANANE","PACK DALAL" ,"PACK CLASSIC" , "PACK PRIVILEGE" ,
#         "PACK NJEGUEMAR'LA", "PACK SOXNA'LA" ,"EPARGNE LIBRE STAFF","PACK TERANGA","EPARGNE YAKHANAAL", "EPARGNE LIBRE DIASPORA CSF"
#     ]

#     for idx, row in df.iterrows():
#         Matricule_Client = row.get('Matricule Client', 'Inconnu')
#         Nom_Client       = row.get('Nom Client',       'Inconnu')
#         Date_Ouverture_Compte       = row.get('Date Ouverture Compte',       'Inconnu')
#         Agence           = row.get('Agence',           'Inconnu')
#         Num_compte       = row.get('N° Compte',        'Inconnu')
#         CC               = row.get('CC',               'Inconnu')
        
#         errors = {
#             "Matricule Client": Matricule_Client,
#             "Nom Client": Nom_Client,
#             "Date Ouverture Compte": Date_Ouverture_Compte ,
#             "Agence":Agence,
#             "N° Compte":Num_compte,
#             "CC":CC,
            
#             "Format du Numéro de Téléphone Invalide": "",
#             "Domaine ou Format de l'Email Invalide": "",
#             "Sexe ou Genre Incorrect ou Manquant pour Entreprise": "",
#             "Représentant Légal Manquant": ""
#         }
#         country_phone_rules = {
#             'Burkina Faso': {'code': '226', 'length': 8},
#             'Côte d\'Ivoire': {'code': '225', 'length': 10},
#             'Guinée': {'code': '224', 'length': 9},
#             'Mali': {'code': '223', 'length': 8},
#             'Sénégal': {'code': '221', 'length': 9},
#             'Togo': {'code': '228', 'length': 8},
#             'Congo': {'code': '242', 'length': 9},
#             'Gabon': {'code': '241', 'length': 8},
#             'France': {'code': '33', 'length': 9},
#             'Maroc': {'code': '212', 'length': 9},
#             'Espagne': {'code': '34', 'length': 9},
#             'Belgique': {'code': '32', 'length': 9}
#         }


#         phone_raw = row.get('Telephone Client', '')

#         phone = re.sub(r'\D', '', str(phone_raw)) if not pd.isna(phone_raw) else ""
        
#         valid_format = False

#         for country, rules in country_phone_rules.items():
#             valid_number_without_code = len(phone) == rules['length']
#             valid_number_with_code = (
#                 phone.startswith(rules['code']) and len(phone) == rules['length'] + len(rules['code']) or
#                 phone.startswith('00' + rules['code']) and len(phone) == rules['length'] + len(rules['code']) + 2 or
#                 phone.startswith('+' + rules['code']) and len(phone) == rules['length'] + len(rules['code']) + 1
#             )
#             if valid_number_without_code or valid_number_with_code:
#                 valid_format = True
#                 break
#         if not valid_format:
#             errors["Format du Numéro de Téléphone Invalide"] = (
#                 "Numéro de téléphone manquant ou format invalide (doit correspondre au format d'un des pays autorisés)"
#             )

#         valid_extensions = r'(com|org|net|edu|gov|mil|int|info|biz|fr|sn|us|uk|ca|de|es|cn|in|br|jp|au|online|tech|site|store|app|io|xyz|club|blog|bank|law|pharma|media|travel|shop|it)$'

#         email = str(row.get('Email Client', '')).strip() if not pd.isna(row.get('Email Client', '')) else ""
        
#         if email:
#             domain = email.split('@')[-1] if "@" in email else None
#             if domain not in valid_domains:
#                 if not re.match(r'^[\w\.-]+@[\w\.-]+\.' + valid_extensions, email):
#                     errors["Domaine ou Format de l'Email Invalide"] = "Format ou domaine de l'email invalide"
#             elif not re.match(r'^[\w\.-]+@[\w\.-]+\.' + valid_extensions, email):
#                 errors["Domaine ou Format de l'Email Invalide"] = "Format de l'email invalide"

#         sexe = str(row.get('SEXE', '')).upper() if not pd.isna(row.get('SEXE', '')) else ""
#         genre_entreprise = str(row.get('Genre Pour Entreprise', '')).upper() if not pd.isna(row.get('Genre Pour Entreprise', '')) else ""
        
#         sexe_normalized = ""
#         genre_entreprise_normalized = ""

#         if sexe in ["F", "FEMININ"]:
#             sexe_normalized = "F"
#         elif sexe in ["M", "MASCULIN"]:
#             sexe_normalized = "M"
#         if genre_entreprise in ["F", "FEMININ"]:
#             genre_entreprise_normalized = "F"
#         elif genre_entreprise in ["M", "MASCULIN"]:
#             genre_entreprise_normalized = "M"

#         if not sexe_normalized and not genre_entreprise_normalized:
#             errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = "Sexe et Genre manquants"
#         elif sexe_normalized and genre_entreprise_normalized and sexe_normalized != genre_entreprise_normalized:
#             errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = "Sexe et Genre ne correspondent pas"
#         elif not sexe_normalized and genre_entreprise_normalized not in ["F", "M"]:
#             errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = "Sexe ou Genre incorrect ou manquant"

#         pack_type = str(row.get('Type de Pack', '')).upper() if not pd.isna(row.get('Type de Pack', '')) else ""
#         representant_legal = str(row.get('Representant Legal', '')).strip() if not pd.isna(row.get('Representant Legal', '')) else ""
#         genre_entreprise = str(row.get('Genre Pour Entreprise', '')).upper() if not pd.isna(row.get('Genre Pour Entreprise', '')) else ""

#         if pack_type not in required_packs:
#             if not representant_legal:
#                 errors["Représentant Légal Manquant"] = "Représentant Légal manquant"
#             if not genre_entreprise:
#                 errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = "Le genre de l'entreprise est requis"
#         if any(errors[column] for column in errors if column not in ["Matricule Client", "Nom Client", "Date Ouverture Compte", "Agence", "N° Compte", "CC"]):
#             invalid_rows.append(errors)

#     if invalid_rows:
#             invalid_df = pd.DataFrame(invalid_rows)
#             invalid_df['Nombre d\'Erreurs'] = invalid_df.apply(
#                 lambda row: sum(1 for value in row[6:] if isinstance(value, str) and value.strip() != ""), axis=1
#             )
#             invalid_df.to_excel(output_path, index=False)
#             return invalid_df
#     else:
#         return pd.DataFrame()  # Retourner un DataFrame vide

def validate_excel(file_path, output_path):

    df = pd.read_excel(file_path)

    invalid_rows = []

#0- Constantes
    # valid_domains = ["gmail.com", "hotmail.fr","hotmail.com", "yahoo.com", "yahoo.fr", "gmail.fr", "outlook.com", "icloud.com", "icloud.fr", "ucad.edu.sn","outlook.fr","cofinacorp.com","live.fr","hotmail.it","gainde2000.sn"]

    for idx, row in df.iterrows():
        Matricule_Client = row.get('Matricule Client', 'Inconnu')
        Nom_Client       = row.get('Nom Client',       'Inconnu')
        Date_Ouverture_Compte       = row.get('Date Ouverture Compte',       'Inconnu')
        Agence           = row.get('Agence',           'Inconnu')
        Num_compte       = row.get('N° Compte',        'Inconnu')
        CC = row["CC"] if pd.notna(row["CC"]) and row["CC"] != "" else row.get("CC2", "Inconnu")
 
        errors = {
            "Matricule Client": Matricule_Client,
            "Nom Client": Nom_Client,
            "Date Ouverture Compte": Date_Ouverture_Compte ,
            "Agence":Agence,
            "N° Compte":Num_compte,
            "CC":CC,
            
            "Format du Numéro de Téléphone Invalide": [],
            "Domaine ou Format de l'Email Invalide": "",
            "Sexe ou Genre Incorrect ou Manquant pour Entreprise": "",
            "Représentant Légal Manquant": ""
        }
        # country_phone_rules = {
        #     'Burkina Faso': {'code': '226', 'length': 8},
        #     'Côte d\'Ivoire': {'code': '225', 'length': 10},
        #     'Guinée': {'code': '224', 'length': 9},
        #     'Mali': {'code': '223', 'length': 8},
        #     'Sénégal': {'code': '221', 'length': 9},
        #     'Togo': {'code': '228', 'length': 8},
        #     'Congo': {'code': '242', 'length': 9},
        #     'Congo (RDC)': {'code': '243', 'length': 9},
        #     'Gabon': {'code': '241', 'length': 8},
        #     'France': {'code': '33', 'length': 9},
        #     'Maroc': {'code': '212', 'length': 9},
        #     'Espagne': {'code': '34', 'length': 9},
        #     'Belgique': {'code': '32', 'length': 9},
        #     'Suisse': {'code': '41', 'length': 9},
        #     'Allemagne': {'code': '49', 'length': 10},
        #     'Italie': {'code': '39', 'length': 10},
        #     'Portugal': {'code': '351', 'length': 9},
        #     'Pays-Bas': {'code': '31', 'length': 9},
        #     'États-Unis': {'code': '1', 'length': 10},
        #     'Canada': {'code': '1', 'length': 10},
        #     'Royaume-Uni': {'code': '44', 'length': 10},
        #     'Afrique du Sud': {'code': '27', 'length': 9},
        #     'Égypte': {'code': '20', 'length': 10},
        #     'Tunisie': {'code': '216', 'length': 8},
        #     'Algérie': {'code': '213', 'length': 9},
        #     'Ghana': {'code': '233', 'length': 9},
        #     'Nigéria': {'code': '234', 'length': 10},
        #     'Kenya': {'code': '254', 'length': 10},
        #     'Tanzanie': {'code': '255', 'length': 9},
        #     'Ouganda': {'code': '256', 'length': 9},
        #     'Inde': {'code': '91', 'length': 10},
        #     'Chine': {'code': '86', 'length': 11},
        #     'Japon': {'code': '81', 'length': 10},
        #     'Brésil': {'code': '55', 'length': 11},
        #     'Argentine': {'code': '54', 'length': 10},
        #     'Mexique': {'code': '52', 'length': 10},
        #     'Australie': {'code': '61', 'length': 9},
        #     'Nouvelle-Zélande': {'code': '64', 'length': 9},
        #     'Turquie': {'code': '90', 'length': 10},
        #     'Russie': {'code': '7', 'length': 10},
        #     'Arabie Saoudite': {'code': '966', 'length': 9},
        #     'Émirats Arabes Unis': {'code': '971', 'length': 9},
        #     'Qatar': {'code': '974', 'length': 8},
        #     'Koweït': {'code': '965', 'length': 8},
        #     'Bahreïn': {'code': '973', 'length': 8},
        #     'Oman': {'code': '968', 'length': 8}
        # }


# #1- Numéro de téléphone
#         # Validation généralisée pour les numéros de téléphone
#         phone_fields = {
#             'Telephone Client': True,  # Obligatoire
#             'TEL_DOM': False,          # Facultatif
#             'TEL_BUR': False           # Facultatif
#         }

#         # Parcours de chaque champ de numéro de téléphone
#         for field_name, is_required in phone_fields.items():
#             phone_raw = row.get(field_name, '')
#             phone_raw = str(phone_raw).strip()  # Éliminer les espaces inutiles
#             phone = re.sub(r'\D', '', phone_raw.split('.')[0]) if not pd.isna(phone_raw) else ""

#             if not phone:
#                 if is_required:
#                     errors["Format du Numéro de Téléphone Invalide"] = (
#                         f"{field_name} est manquant ou vide (ce champ est obligatoire)."
#                     )
#                 continue  # Passe au champ suivant si facultatif et vide

#             valid_format = False

#             for country, rules in country_phone_rules.items():
#                 valid_number_without_code = len(phone) == rules['length']
#                 valid_number_with_code = (
#                     phone.startswith(rules['code']) and len(phone) == rules['length'] + len(rules['code']) or
#                     phone.startswith('00' + rules['code']) and len(phone) == rules['length'] + len(rules['code']) + 2 or
#                     phone.startswith('+' + rules['code']) and len(phone) == rules['length'] + len(rules['code']) + 1
#                 )
#                 if valid_number_without_code or valid_number_with_code:
#                     valid_format = True
#                     break

#             if not valid_format:
#                 errors["Format du Numéro de Téléphone Invalide"] = (
#                     f"{field_name} '{phone_raw}' a un format invalide : indicatif et/ou taille incorrects."
#                 )

#         if not errors["Format du Numéro de Téléphone Invalide"]:
#             errors["Format du Numéro de Téléphone Invalide"] = ""
            
        # Définition des champs contenant des numéros de téléphone
        phone_fields = {
            'Telephone Client': True,  # Obligatoire
            'TEL_DOM': False,          # Facultatif
            'TEL_BUR': False           # Facultatif
        }

        for field_name, is_required in phone_fields.items():
            phone_raw = str(row.get(field_name, '')).strip()

            if not phone_raw:
                if is_required:
                    errors["Format du Numéro de Téléphone Invalide"] = (
                        f"{field_name} est manquant ou vide (ce champ est obligatoire)."
                    )
                continue  # Passe au champ suivant si facultatif et vide

            try:
                # Suppression des espaces et normalisation
                phone_number = phonenumbers.parse(phone_raw, None)

                # Vérification si le numéro est valide
                if not phonenumbers.is_valid_number(phone_number):
                    errors["Format du Numéro de Téléphone Invalide"] = (
                        f"{field_name} '{phone_raw}' a un format invalide."
                    )
            except phonenumbers.phonenumberutil.NumberParseException:
                errors["Format du Numéro de Téléphone Invalide"] = (
                    f"{field_name} '{phone_raw}' ne peut pas être interprété comme un numéro valide."
                )

        if not errors.get("Format du Numéro de Téléphone Invalide"):
            errors["Format du Numéro de Téléphone Invalide"] = ""
       
#2- Adresse mail
        # # Liste des extensions valides pour les emails
        # valid_extensions = r'(com|org|net|edu|gov|mil|int|info|biz|fr|sn|us|uk|ca|de|es|cn|in|br|jp|au|online|tech|site|store|app|io|xyz|club|blog|bank|law|pharma|media|travel|shop|it|ru)$'

        # # Récupération et nettoyage de l'email
        # email = str(row.get('Email Client', '')).strip() if not pd.isna(row.get('Email Client', '')) else ""

        # # Initialisation des erreurs
        # email_errors = []


        # if not email:
        #     # Erreur si l'email est absent
        #     errors["Domaine ou Format de l'Email Invalide"] = "Adresse email obligatoire manquante."
        # else:
        #     # Vérification de la présence de "@" dans l'email
        #     if "@" not in email:
        #         email_errors.append("Adresse email invalide : le symbole '@' est manquant.")
        #     else:
        #         # Séparation de la partie locale et du domaine
        #         local_part, domain = email.split('@', 1)

        #         # Vérification du domaine
        #         if "." not in domain:
        #             email_errors.append("Adresse email invalide : le domaine est incorrect (pas de point).")
        #         else:
        #             # Vérification de l'extension
        #             extension = domain.split('.')[-1]
        #             if not re.match(valid_extensions, extension):
        #                 email_errors.append(f"Extension du domaine invalide : .{extension} n'est pas autorisée.")
                
        #         # Vérification du format général de l'email
        #         if not re.match(r'^[\w\.-]+@[\w\.-]+\.' + valid_extensions, email):
        #             email_errors.append("Format général de l'adresse email invalide.")

        # # Ajout des erreurs au dictionnaire principal si elles existent
        # if email_errors:
        #     errors["Domaine ou Format de l'Email Invalide"] = " | ".join(email_errors)
        
        # Récupération et nettoyage de l'email
        email = str(row.get('Email Client', '')).strip() if not pd.isna(row.get('Email Client', '')) else ""

        # Initialisation des erreurs
        email_errors = []

        if not email:
            errors["Domaine ou Format de l'Email Invalide"] = "Adresse email obligatoire manquante."
        else:
            # Vérification du format général avec la bibliothèque validators
            if not validators.email(email):
                email_errors.append("Format général de l'adresse email invalide.")

            # Extraction du domaine avec tldextract
            extracted = tldextract.extract(email)
            domain = f"{extracted.domain}.{extracted.suffix}" if extracted.suffix else ""

            if not domain:
                email_errors.append("Domaine email invalide.")
            else:
                # Vérification si le TLD est valide
                if not extracted.suffix:
                    email_errors.append("Extension de domaine invalide.")

        # Ajout des erreurs au dictionnaire principal si elles existent
        if email_errors:
            errors["Domaine ou Format de l'Email Invalide"] = " | ".join(email_errors)

#3- Genre
        # Récupération et nettoyage des champs
        sexe = str(row.get('SEXE', '')).strip().upper() if not pd.isna(row.get('SEXE', '')) else ""
        genre_entreprise = str(row.get('Genre Pour Entreprise', '')).strip().upper() if 'Genre Pour Entreprise' in row and not pd.isna(row.get('Genre Pour Entreprise', '')) else ""
        type_pack = str(row.get('Type de Pack', '')).strip().upper() if not pd.isna(row.get('Type de Pack', '')) else ""

        sexe_normalized = ""
        genre_entreprise_normalized = ""

        # Normalisation des valeurs pour "SEXE"
        if sexe in ["F", "FEMININ", "FEMME"]:
            sexe_normalized = "F"
        elif sexe in ["M", "MASCULIN", "HOMME"]:
            sexe_normalized = "M"

        # Normalisation des valeurs pour "Genre Pour Entreprise" (si présent)
        if genre_entreprise in ["F", "FEMININ", "FEMME"]:
            genre_entreprise_normalized = "F"
        elif genre_entreprise in ["M", "MASCULIN", "HOMME"]:
            genre_entreprise_normalized = "M"

        # Validation en fonction du "Type de Pack"
        if type_pack == "Personne physique":
            if not sexe_normalized:
                errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = (
                    "Sexe obligatoire manquant pour le pack 'Personne physique'."
                )
            elif genre_entreprise and not genre_entreprise_normalized:
                errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = (
                    f"Le genre pour entreprise '{row.get('Genre Pour Entreprise', '')}' est incorrect."
                )
            elif sexe_normalized and genre_entreprise_normalized and sexe_normalized != genre_entreprise_normalized:
                errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = (
                    "Sexe et Genre Pour Entreprise ne correspondent pas."
                )
        else:
            # Si le type de pack n'est pas "Personne physique", on n'exige pas le sexe
            if genre_entreprise and not genre_entreprise_normalized:
                errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = (
                    f"Le genre pour entreprise '{row.get('Genre Pour Entreprise', '')}' est incorrect."
                )
            elif sexe_normalized and genre_entreprise_normalized and sexe_normalized != genre_entreprise_normalized:
                errors["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] = (
                    "Sexe et Genre Pour Entreprise ne correspondent pas."
                )


#4- Représentant Légale
        pack_type = str(row.get('Type de Pack', '')).upper() if not pd.isna(row.get('Type de Pack', '')) else ""
        representant_legal = str(row.get('Representant Legal', '')).strip() if not pd.isna(row.get('Representant Legal', '')) else ""

        # Vérification des erreurs
        if pack_type == "Personne morale":
            # Le représentant légal est obligatoire pour les "Personne Morale"
            if not representant_legal:
                errors["Représentant Légal Manquant"] = "Représentant Légal manquant pour le pack 'Personne Morale'."
              
        if any(errors[column] for column in errors if column not in ["Matricule Client", "Nom Client", "Date Ouverture Compte", "Agence", "N° Compte", "CC"]):
            invalid_rows.append(errors)

#5- Fichier retourné
    if invalid_rows:
        invalid_df = pd.DataFrame(invalid_rows)
        invalid_df.to_excel(output_path, index=False)
        return invalid_df
    else:
        return pd.DataFrame()  # Retourner un DataFrame vide

