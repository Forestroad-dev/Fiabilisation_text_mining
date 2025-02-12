from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
from io import BytesIO
import os
from fiabilisation import validate_excel  # Assurez-vous que cette fonction est bien définie
import tempfile
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autoriser toutes les origines (vous pouvez spécifier les URL précises pour plus de sécurité)
    allow_credentials=True,
    allow_methods=["*"],  # Autoriser toutes les méthodes
    allow_headers=["*"],  # Autoriser tous les en-têtes
)

file_store = {}

@app.get("/")
async def root():
    return {"message": "Bienvenue dans mon API!"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return JSONResponse(content={"message": "Pas de favicon disponible."})

@app.post("/validate-excel/")
async def validate_excel_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xls', '.xlsx')):
        return JSONResponse(
            content={"message": "Format de fichier non pris en charge. Veuillez fournir un fichier Excel.",
                     "file_name": file.filename },
            status_code=400
        )
    
    # Création d'un fichier temporaire pour l'upload
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    try:
        temp_file.write(await file.read())
        temp_file.close()

        # Lecture du fichier Excel
        df = pd.read_excel(temp_file.name)

        # Vérification des colonnes obligatoires
        required_columns = ["CC", "Agence"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return JSONResponse(
                content={"message": f"Colonnes obligatoires manquantes : {missing_columns}",
                         "file_name": file.filename},
                status_code=400
            )

        invalid_data_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        # invalid_data = validate_excel(temp_file.name, invalid_data_file.name)
        
        # Exécuter la validation
        try:
            invalid_data = validate_excel(temp_file.name, invalid_data_file.name)
        except Exception as e:
            return JSONResponse(content={"message": f"Erreur lors de la validation : {e}",
                                         "file_name": file.filename,
                                         }, status_code=400)
        
        
        # Vérifier si des erreurs existent
        if invalid_data.empty:
            return JSONResponse(content={
                "message": "Aucune erreur détectée dans le fichier fourni.",
                "file_name": file.filename
            }, status_code=200)

        # Sauvegarder le fichier des données invalides pour téléchargement
        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        invalid_data_path = os.path.join(temp_dir, f"invalid_data_{file.filename}")
        invalid_data.to_excel(invalid_data_path, index=False)
        
        # Nombre total de lignes
        total_rows = len(df)

        # Nombre de lignes avec des erreurs
        rows_with_errors = len(invalid_data)

        total_errors = 0
        error_counts = invalid_data.apply(lambda x: x.astype(str).str.strip() != "").sum()
        filtered_errors = {column: count for column, count in error_counts.items() if column not in ["Matricule Client", "Nom Client", "Date Ouverture Compte", "Agence", "N° Compte", "CC","Nombre d'Erreurs"]}

        # Résumé des erreurs par catégorie
        error_summary = [{"column": column, "count": count} for column, count in filtered_errors.items()]
        total_errors = sum(filtered_errors.values())


        # Création du résumé des erreurs par CC
        specific_error_columns = [
            "Format du Numéro de Téléphone Invalide",
            "Domaine ou Format de l'Email Invalide",
            "Sexe ou Genre Incorrect ou Manquant pour Entreprise",
            "Représentant Légal Manquant"
        ]

        # Calcul des erreurs spécifiques pour chaque CC en fonction de l'agence
        invalid_data["Total Erreurs"] = invalid_data[specific_error_columns].fillna('').apply(lambda row: (row != "").sum(), axis=1)

        # Groupe par CC et Agence, et calcul des erreurs spécifiques pour chaque CC dans chaque agence
        cc_error_counts = invalid_data.groupby(["CC", "Agence"])[specific_error_columns].apply(lambda group: (group != "").sum()).reset_index()

        # Calcul des erreurs totales par CC dans chaque agence
        cc_error_counts["Total Erreurs Agence"] = cc_error_counts[specific_error_columns].sum(axis=1)

        # Calcul du total des erreurs globales pour chaque CC (toutes agences confondues)
        cc_total_errors = (
            cc_error_counts.groupby("CC")["Total Erreurs Agence"].sum().reset_index()
        )
        cc_total_errors = cc_total_errors.rename(columns={"Total Erreurs Agence": "Total Erreurs"})

        # Ajouter le total des erreurs globales pour chaque CC au DataFrame
        cc_error_counts = pd.merge(cc_error_counts, cc_total_errors, on="CC", how="left")

        # Recalculer le total des erreurs globales (tous CC et toutes agences confondus)
        total_errors_global = cc_error_counts["Total Erreurs"].sum()

        # Calcul du pourcentage pour chaque CC (par rapport au total global des erreurs)
        cc_error_counts["Pourcentage"] = cc_error_counts["Total Erreurs"] / total_errors_global * 100 if total_errors_global > 0 else 0

        # Calcul du pourcentage des erreurs du CC dans l'agence par rapport aux erreurs totales de l'agence
        cc_error_counts["Pourcentage Par Agence"] = cc_error_counts.apply(
            lambda row: (row["Total Erreurs Agence"] / cc_error_counts[cc_error_counts["Agence"] == row["Agence"]]["Total Erreurs Agence"].sum() * 100)
            if row["Total Erreurs Agence"] > 0 else 0,
            axis=1
        )

        # Ajouter les CC manquants (sans erreurs) pour garantir que tous les CC sont inclus
        all_cc = df[["CC", "Agence"]].drop_duplicates()  # Récupère tous les CC uniques et leurs agences
        cc_error_counts = pd.merge(
            all_cc,  # Inclure les informations d'agence
            cc_error_counts, 
            on=["CC", "Agence"],  # Fusion sur CC et Agence
            how="left"
        ).fillna(0)  # Remplir les valeurs manquantes avec 0


        # Trier les résultats par pourcentage
        cc_error_counts = cc_error_counts.sort_values(by="Pourcentage", ascending=False).reset_index(drop=True)


        # Résumé des erreurs par Agence
        agence_error_counts = invalid_data.groupby("Agence")[specific_error_columns].apply(lambda group: (group != "").sum()).reset_index()
        agence_error_counts["Total Erreurs"] = agence_error_counts[specific_error_columns].sum(axis=1)

        # Supprimer les doublons basés sur CC et Agence
        unique_cc_per_agence = df[["CC", "Agence"]].drop_duplicates()

        # Calcul du nombre de CC par agence
        cc_per_agence = unique_cc_per_agence.groupby("Agence")["CC"].nunique().reset_index()

        # Renommer la colonne pour plus de clarté
        cc_per_agence = cc_per_agence.rename(columns={"CC": "Nombre de CC"})

        # Ajouter les agences manquantes (même celles sans erreur) avec un total de 0
        all_agences = df["Agence"].unique()
        agence_error_counts = pd.merge(
            pd.DataFrame({"Agence": all_agences}),
            agence_error_counts,
            on="Agence",
            how="left"
        ).fillna(0)

        # Fusionner le nombre de CC par agence
        agence_error_counts = pd.merge(agence_error_counts, cc_per_agence, on="Agence", how="left").fillna(0)

        # Calcul du pourcentage d'erreurs par agence
        total_errors_by_agence = agence_error_counts["Total Erreurs"].sum()
        agence_error_counts["Pourcentage"] = (
            (agence_error_counts["Total Erreurs"] / total_errors_by_agence) * 100 if total_errors_by_agence > 0 else 0
        )

        # Trier les agences par pourcentage décroissant
        agence_error_counts = agence_error_counts.sort_values(by="Pourcentage", ascending=False).reset_index(drop=True)

        # Résultat des erreurs
        
        # Convertir NaN en 0 ou une autre valeur acceptable
        cc_error_counts = cc_error_counts.fillna(0)
        agence_error_counts = agence_error_counts.fillna(0)

        
                # Inclure tous les CC avec ou sans erreurs
        cc_with_errors = cc_error_counts[cc_error_counts["Total Erreurs"] > 0]["CC"].unique()  # CC avec des erreurs

        # Calculer le pourcentage des CC avec des erreurs
        percentage_cc_with_errors = round((len(cc_with_errors) / len(all_cc)) * 100 if len(all_cc) > 0 else 0)

        result = {
            "file_name": os.path.splitext(file.filename)[0],
            "download_link": f"/download-invalid-file/{os.path.basename(file.filename)}",  # Inclure le nom du fichier original
            "total_rows": total_rows,
            "rows_with_errors": rows_with_errors,
            "total_errors": total_errors,
            "error_summary": error_summary,
            "cc_error_counts": cc_error_counts.to_dict(orient="records"),
            "agence_error_counts": agence_error_counts.to_dict(orient="records"),
            "percentage_cc_with_errors": percentage_cc_with_errors,
            "percentage_agences_with_errors": round((len(agence_error_counts[agence_error_counts["Total Erreurs"] > 0]) / len(all_agences)) * 100)
        }

        error_summary_df = pd.DataFrame(error_summary)  
        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, "erreurs_resume_latest.xlsx")
        error_summary_df.to_excel(file_path, index=False)
        invalid_data_path = os.path.join(temp_dir, f"invalid_data_{file.filename}")
        file_store["latest_file"] = invalid_data_path



        # # Générer un lien pour télécharger le fichier des erreurs
        # download_link = "/download-invalid-file/"
        
        # Retourner un fichier Excel avec les lignes invalides en option
        return JSONResponse(content={
            "message": "Validation réussie",
            "download_link": "/download-invalid-file/",
            "result": result  # Ajout des résultats détaillés
        })

        
    except Exception as e:
        return JSONResponse(content={"message": f"Erreur : {e}"}, status_code=500)

    finally:
        os.unlink(temp_file.name) 

@app.get("/download-invalid-file/")
async def download_invalid_file():
    # Récupérer le chemin du fichier à partir du dictionnaire global
    invalid_data_path = file_store.get("latest_file")

    if not invalid_data_path or not os.path.isfile(invalid_data_path):
        return JSONResponse(
            content={"message": "Aucun fichier d'erreurs disponible pour le téléchargement."},
            status_code=404
        )

    # Retourner le fichier
    return FileResponse(
        invalid_data_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=os.path.basename(invalid_data_path),
        headers={"Content-Disposition": f'attachment; filename="{os.path.basename(invalid_data_path)}"'}
    )
