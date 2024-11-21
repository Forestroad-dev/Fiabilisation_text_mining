import streamlit as st
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fiabilisation import validate_excel  # Importer la fonction de validation

# app = FastAPI()

# @app.get("/")
# async def home():
#     return {"message": "Bienvenue sur l'API de validation des comptes client"}


# # Route pour l'upload du fichier
# @app.post("/upload/")
# async def upload_file(file: UploadFile = File(...)):
#     try:
#         # Lire le fichier Excel
#         df = pd.read_excel(file.file)
#         return {"message": f"Fichier chargé avec {df.shape[0]} lignes", "data_preview": df.head().to_html()}
#     except Exception as e:
#         return {"error": f"Erreur lors de la lecture du fichier : {e}"}

# # Route pour traiter et valider les données
# @app.post("/validate/")
# async def validate_and_generate(file: UploadFile = File(...)):
#     try:
#         # Charger et valider les données
#         df = pd.read_excel(file.file)
#         output_path = "invalid_rows.xlsx"
#         invalid_data = validate_excel(file.file, output_path)
        
#         # Calculer les erreurs
#         error_counts = invalid_data.apply(lambda x: x != "").sum()
#         filtered_errors = {column: count for column, count in error_counts.items()
#                            if count > 0 and column not in ["Matricule Client", "Nom Client", "Agence", "N° Compte", "CC"]}
        
#         # Créer un graphique
#         fig, ax = plt.subplots()
#         categories = list(filtered_errors.keys())
#         counts = list(filtered_errors.values())
#         ax.bar(categories, counts, color='skyblue')
#         ax.set_title("Nombre d'erreurs par catégorie")
#         ax.set_xlabel("Catégorie")
#         ax.set_ylabel("Nombre d'erreurs")
#         ax.set_xticks(range(len(categories)))
#         ax.set_xticklabels(categories, rotation=45, ha="right")
        
#         # Sauvegarder le graphique en mémoire et retourner le fichier image
#         img_io = BytesIO()
#         plt.savefig(img_io, format='png')
#         img_io.seek(0)
        
#         # Renvoi du graphique au format image
#         return HTMLResponse(content=f'<img src="data:image/png;base64,{img_io.getvalue().encode("base64")}" />')
    
#     except Exception as e:
#         return {"error": f"Erreur lors de la validation : {e}"}

# # Route pour télécharger le fichier d'erreurs
# @app.get("/download/")
# async def download_file():
#     try:
#         return FileResponse("invalid_rows.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="invalid_rows.xlsx")
#     except Exception as e:
#         return {"error": f"Erreur lors du téléchargement du fichier : {e}"}


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

        # Filtrer uniquement les colonnes pertinentes pour les erreurs
        error_columns = [col for col in invalid_data.columns if col not in ["Matricule Client", "Nom Client", "Agence", "N° Compte", "CC"]]

        # Calculer le nombre d'erreurs par ligne
        invalid_data["Total Erreurs"] = invalid_data[error_columns].apply(lambda row: (row != "").sum(), axis=1)

        cc_error_counts = invalid_data.groupby("CC")["Total Erreurs"].sum().reset_index()

        # Calculer le total global des erreurs
        total_errors = cc_error_counts["Total Erreurs"].sum()

        # Ajouter une colonne pourcentage
        cc_error_counts["Pourcentage"] = (cc_error_counts["Total Erreurs"] / total_errors) * 100

        # Ajouter une ligne pour le total global des erreurs
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
        
        # Diagramme circulaire des pourcentages avec légende
        st.subheader("Diagramme circulaire des pourcentages")
        fig1, ax1 = plt.subplots()

        # Exclusion explicite de la ligne "Total"
        data_for_pie = cc_error_counts[cc_error_counts["CC"] != "Total"]

        # Création du diagramme sans étiquettes
        wedges, texts = ax1.pie(
            data_for_pie["Pourcentage"],  # Utiliser uniquement les pourcentages sans le total
            labels=None,  # Pas de labels sur le graphique
            startangle=90,
            colors=plt.cm.Paired.colors
        )

        # Ajout de la légende
        ax1.legend(
            wedges, 
            data_for_pie["CC"], 
            title="Catégories",
            loc="center left", 
            bbox_to_anchor=(1, 0, 0.5, 1)  # Positionner la légende à droite
        )

        ax1.axis('equal')  # Cercle parfait

        # Afficher le diagramme
        st.pyplot(fig1)

        # Podium : diagramme en barres des 3 premiers (hors "Total")
        st.subheader("Podium des CC avec le plus d'erreurs")
        top_3 = cc_error_counts[cc_error_counts["CC"] != "Total"].iloc[:3]  # Exclure "Total"
        fig2, ax2 = plt.subplots()
        ax2.bar(top_3["CC"], top_3["Total Erreurs"], color=['gold', 'silver', 'brown'])
        ax2.set_title("Top 3 des CC avec le plus d'erreurs")
        ax2.set_ylabel("Total Erreurs")
        ax2.set_xlabel("CC")
        st.pyplot(fig2)
        
        # Podium : diagramme en barres des 3 CC avec le moins d'erreurs (hors "Total")
        st.subheader("Podium des CC avec le moins d'erreurs")
        bottom_3 = cc_error_counts[cc_error_counts["CC"] != "Total"].sort_values("Total Erreurs").iloc[:3]  # Exclure "Total" et trier par erreurs croissantes
        fig2, ax2 = plt.subplots()
        ax2.bar(bottom_3["CC"], bottom_3["Total Erreurs"], color=['lightgreen', 'lightblue', 'lightcoral'])
        ax2.set_title("Top 3 des CC avec le moins d'erreurs")
        ax2.set_ylabel("Total Erreurs")
        ax2.set_xlabel("CC")
        st.pyplot(fig2)


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
