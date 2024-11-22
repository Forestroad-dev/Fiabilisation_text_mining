import streamlit as st
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fiabilisation import validate_excel  # Importer la fonction de validation

# Injecter le CSS personnalisé
with open("styles.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

# Titre et interface
st.title("Validation des Comptes Client")

# Interface pour le téléchargement de fichier
uploaded_file = st.file_uploader("Téléchargez un fichier Excel", type=["xlsx"])

if uploaded_file is not None:
    # Lecture du fichier téléchargé
    try:
        df = pd.read_excel(uploaded_file)
        st.write(f"**Aperçu du fichier chargé : {df.shape[0]}**")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
        st.stop()

    # Spécifier le chemin de sortie pour enregistrer les erreurs
    output_path = "invalid_rows.xlsx"
    
    # Exécuter la validation
    st.info("Validation en cours, veuillez patienter...")
    try:
        invalid_data = validate_excel(uploaded_file, output_path)
    except Exception as e:
        st.error(f"Erreur lors de la validation : {e}")
        st.stop()
    
    total_errors = 0
    error_counts = invalid_data.apply(lambda x: x != "").sum()
    filtered_errors = {column: count for column, count in error_counts.items()
                    if count > 0 and column not in ["Matricule Client", "Nom Client", "Agence", "N° Compte", "CC"]}

    # Affichage des erreurs
    st.subheader("Résumé des erreurs par catégorie")
    for column, count in filtered_errors.items():
        st.write(f"**{column}** : {count} erreurs")
        total_errors += count

    # Création du diagramme en barres
    if filtered_errors:
        st.subheader("Diagramme des erreurs par catégorie")
        fig, ax = plt.subplots()
        categories = list(filtered_errors.keys())
        counts = list(filtered_errors.values())

        ax.bar(categories, counts, color='skyblue')
        ax.set_title("Nombre d'erreurs par catégorie")
        ax.set_xlabel("Catégorie")
        ax.set_ylabel("Nombre d'erreurs")
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha="right")

        # Affichage dans Streamlit
        st.pyplot(fig)
        
        # Affichage du total des erreurs
        st.write(f"**Total des erreurs : {total_errors}**")
        
        # Afficher les lignes invalides
        st.write(f"**Nombre total de d'erreurs par matricules : {invalid_data.shape[0]}**")
        st.dataframe(invalid_data)

        # Ajouter un résumé des erreurs par CC
        st.subheader("Résumé des erreurs par CC")

        # Erreurs spécifiques à compter
        specific_error_columns = [
            "Format du Numéro de Téléphone Invalide",
            "Domaine ou Format de l'Email Invalide",
            "Sexe ou Genre Incorrect ou Manquant pour Entreprise",
            "Représentant Légal Manquant"
        ]

        # Calculer le nombre d'erreurs par ligne pour chaque type d'erreur spécifique
        invalid_data["Total Erreurs"] = invalid_data[specific_error_columns].apply(lambda row: (row != "").sum(), axis=1)

        # Calculer le nombre d'occurrences de chaque type d'erreur par CC
        cc_error_counts = invalid_data.groupby("CC")[specific_error_columns].apply(lambda group: (group != "").sum()).reset_index()

        # Calculer le total des erreurs par CC
        cc_error_counts["Total Erreurs"] = cc_error_counts[specific_error_columns].sum(axis=1)

        # Obtenir la liste complète des CC présents dans le fichier
        all_cc = df["CC"].unique()

        # Compléter cc_error_counts avec les CC sans erreurs spécifiques (si nécessaire)
        cc_error_counts = pd.merge(
            pd.DataFrame({"CC": all_cc}),  # Crée un DataFrame avec tous les CC
            cc_error_counts,  # Ajoute les erreurs existantes
            on="CC",  # Fusionne sur la colonne "CC"
            how="left"  # Garder tous les CC même ceux sans erreurs
        ).fillna(0)  # Remplir les CC sans erreurs avec 0

        # Calculer de nouveau le total global des erreurs
        total_errors = cc_error_counts["Total Erreurs"].sum()

        # Ajouter une colonne pourcentage, en évitant la division par zéro
        cc_error_counts["Pourcentage"] = (cc_error_counts["Total Erreurs"] / total_errors) * 100 if total_errors > 0 else 0

        # Ajouter la ligne "Total"
        cc_error_counts = pd.concat([
            cc_error_counts,
            pd.DataFrame({
                "CC": ["Total"],
                "Total Erreurs": [total_errors],
                "Pourcentage": [100]  # Le total représente toujours 100 %
            })
        ], ignore_index=True)

        # Trier les résultats par nombre d'erreurs, décroissant
        cc_error_counts = cc_error_counts.sort_values(by="Total Erreurs", ascending=False, ignore_index=True)

        # Afficher le tableau des erreurs par "CC"
        st.write(cc_error_counts)
        
        # Calculer le pourcentage de CC ayant commis des erreurs
        cc_with_errors = cc_error_counts[cc_error_counts["Total Erreurs"] > 0].shape[0]  # CC avec des erreurs
        total_cc = len(all_cc)  # Total des CC
        percentage_cc_with_errors = (cc_with_errors / total_cc) * 100 if total_cc > 0 else 0

        # Afficher le pourcentage de CC ayant des erreurs
        st.markdown(f"### Pourcentage de CC ayant commis des erreurs : **{percentage_cc_with_errors:.2f}%**")


        # Ajouter un résumé des erreurs par Agence
        st.subheader("Résumé des erreurs par Agence")

        # Erreurs spécifiques à compter
        specific_error_columns = [
            "Format du Numéro de Téléphone Invalide",
            "Domaine ou Format de l'Email Invalide",
            "Sexe ou Genre Incorrect ou Manquant pour Entreprise",
            "Représentant Légal Manquant"
        ]

        # Calculer le nombre d'erreurs par ligne pour chaque type d'erreur spécifique
        invalid_data["Total Erreurs"] = invalid_data[specific_error_columns].apply(lambda row: (row != "").sum(), axis=1)

        # Calculer le nombre d'occurrences de chaque type d'erreur par Agence
        agence_error_counts = invalid_data.groupby("Agence")[specific_error_columns].apply(lambda group: (group != "").sum()).reset_index()

        # Calculer le total des erreurs par agence
        agence_error_counts["Total Erreurs"] = agence_error_counts[specific_error_columns].sum(axis=1)

        # Obtenir la liste complète des Agences présentes dans le fichier
        all_agences = df["Agence"].unique()

        # Compléter agence_error_counts avec les Agences sans erreurs spécifiques (si nécessaire)
        agence_error_counts = pd.merge(
            pd.DataFrame({"Agence": all_agences}),  # Crée un DataFrame avec toutes les Agences
            agence_error_counts,  # Ajoute les erreurs existantes
            on="Agence",  # Fusionne sur la colonne "Agence"
            how="left"  # Garder toutes les Agences même celles sans erreurs
        ).fillna(0)  # Remplir les Agences sans erreurs avec 0

        # Calculer de nouveau le total global des erreurs
        total_errors = agence_error_counts["Total Erreurs"].sum()

        # Ajouter une colonne pourcentage, en évitant la division par zéro
        agence_error_counts["Pourcentage"] = (agence_error_counts["Total Erreurs"] / total_errors) * 100 if total_errors > 0 else 0

        # Ajouter la ligne "Total"
        agence_error_counts = pd.concat([
            agence_error_counts,
            pd.DataFrame({
                "Agence": ["Total"],
                "Total Erreurs": [total_errors],
                "Pourcentage": [100]  # Le total représente toujours 100 %
            })
        ], ignore_index=True)

        # Trier les résultats par nombre d'erreurs, décroissant
        agence_error_counts = agence_error_counts.sort_values(by="Total Erreurs", ascending=False, ignore_index=True)

        # Afficher le tableau des erreurs par "Agence"
        st.write(agence_error_counts)
        
        # Calculer le pourcentage d'agences ayant commis des erreurs
        agences_with_errors = agence_error_counts[agence_error_counts["Total Erreurs"] > 0].shape[0]  # Agences avec des erreurs
        total_agences = len(all_agences)  # Total des agences
        percentage_agences_with_errors = (agences_with_errors / total_agences) * 100 if total_agences > 0 else 0

        # Afficher le pourcentage d'agences ayant des erreurs
        st.markdown(f"### Pourcentage d'agences ayant commis des erreurs : **{percentage_agences_with_errors:.2f}%**")

        # Télécharger le fichier contenant les erreurs
        with open(output_path, "rb") as file:
            st.download_button(
                label="Télécharger les lignes invalides",
                data=file,
                file_name="invalid_rows.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.success("Toutes les lignes répondent aux critères de validation.")
else:
    st.info("Veuillez télécharger un fichier Excel pour commencer la validation.")
