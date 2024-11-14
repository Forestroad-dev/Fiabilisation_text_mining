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

# Si un fichier est téléchargé
if uploaded_file is not None:
    # Spécifier le chemin de sortie pour enregistrer les erreurs
    output_path = "invalid_rows.xlsx"
    
    # Exécuter la validation
    invalid_data = validate_excel(uploaded_file, output_path)
    
    # Afficher les résultats
    if isinstance(invalid_data, pd.DataFrame):
        # # Compter le nombre d'erreurs pour chaque colonne
        # error_counts = invalid_data.apply(lambda x: x != "").sum()
        
        # # Afficher le nombre total d'erreurs pour chaque type
        # st.subheader("Résumé des erreurs")
        # for column, count in error_counts.items():
        #     if column != "Matricule Client":  # Exclure la colonne Matricule Client si elle n'est pas utilisée pour les erreurs
        #         st.write(f"{column}: {count} erreurs")
        
        st.write(f"Nombre de lignes avec erreurs: {invalid_data.shape[0]}")
        st.dataframe(invalid_data)  # Affiche les lignes invalides dans un tableau Streamlit
        
        # Lien pour télécharger le fichier avec les erreurs
        with open(output_path, "rb") as file:
            btn = st.download_button(
                label="Télécharger les lignes invalides",
                data=file,
                file_name="invalid_rows.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.success("Toutes les lignes répondent aux critères de validation.")
