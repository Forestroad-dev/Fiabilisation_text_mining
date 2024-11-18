import streamlit as st
import pandas as pd
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
    
    # Afficher les résultats
    if isinstance(invalid_data, pd.DataFrame):
        # Résumé des erreurs par colonne
        st.subheader("Résumé des erreurs par catégorie")
        total_errors = 0
        error_counts = invalid_data.apply(lambda x: x != "").sum()
        for column, count in error_counts.items():
            if count > 0 and column not in ["Matricule Client", "Nom Client", "Agence", "N° Compte", "CC"]:
                st.write(f"**{column}** : {count} erreurs")
                total_errors += count
        
        
        # Affichage du total des erreurs
        st.write(f"**Total des erreurs : {total_errors}**")
        
        # Afficher les lignes invalides
        st.write(f"**Nombre total de d'erreurs par matricules : {invalid_data.shape[0]}**")
        st.dataframe(invalid_data)

        # Ajouter un résumé des erreurs par CC
        st.subheader("Résumé des erreurs par CC")

        # Filtrer uniquement les colonnes pertinentes pour les erreurs
        error_columns = [col for col in invalid_data.columns if col not in ["Matricule Client", "Nom Client", "Agence", "N° Compte", "CC"]]

        # Calculer le nombre d'erreurs par ligne
        invalid_data["Total Erreurs"] = invalid_data[error_columns].apply(lambda row: (row != "").sum(), axis=1)

        # Grouper par "CC" et calculer le total des erreurs
        cc_error_counts = invalid_data.groupby("CC")["Total Erreurs"].sum().reset_index()

        # Trier les résultats par nombre d'erreurs, décroissant
        cc_error_counts = cc_error_counts.sort_values(by="Total Erreurs", ascending=False)

        # Afficher le tableau des erreurs par "CC"
        st.write(cc_error_counts)


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
