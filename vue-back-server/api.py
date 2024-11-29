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
            content={"message": "Format de fichier non pris en charge. Veuillez fournir un fichier Excel."},
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
                content={"message": f"Colonnes obligatoires manquantes : {missing_columns}"},
                status_code=400
            )

        invalid_data_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        # invalid_data = validate_excel(temp_file.name, invalid_data_file.name)
        
        # Exécuter la validation
        try:
            invalid_data = validate_excel(temp_file.name, invalid_data_file.name)
        except Exception as e:
            return JSONResponse(content={"message": f"Erreur lors de la validation : {e}"}, status_code=400)
        
        
        # Nombre total de lignes
        total_rows = len(df)

        # Nombre de lignes avec des erreurs
        rows_with_errors = len(invalid_data)

        total_errors = 0
        error_counts = invalid_data.apply(lambda x: x.astype(str).str.strip() != "").sum()
        filtered_errors = {column: count for column, count in error_counts.items()
                            if count > 0 and column not in ["Matricule Client", "Nom Client", "Agence", "N° Compte", "CC"]}

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

        
        invalid_data["Total Erreurs"] = invalid_data[specific_error_columns].apply(lambda row: (row != "").sum(), axis=1)
        cc_error_counts = invalid_data.groupby("CC")[specific_error_columns].apply(lambda group: (group != "").sum()).reset_index()
        cc_error_counts["Total Erreurs"] = cc_error_counts[specific_error_columns].sum(axis=1)
       
        # Calculer le total des erreurs par CC
        all_cc = df["CC"].unique()
        cc_error_counts = pd.merge(
            pd.DataFrame({"CC": all_cc}),
            cc_error_counts,
            on="CC",
            how="left"
        ).fillna(0)

        total_errors_by_cc = cc_error_counts["Total Erreurs"].sum()
        
        cc_error_counts["Pourcentage"] = (cc_error_counts["Total Erreurs"] / total_errors_by_cc) * 100 if total_errors_by_cc > 0 else 0

        cc_error_counts = cc_error_counts.sort_values(by="Pourcentage", ascending=False).reset_index(drop=True)
        
        # Résumé des erreurs par Agence
        agence_error_counts = invalid_data.groupby("Agence")[specific_error_columns].apply(lambda group: (group != "").sum()).reset_index()
        agence_error_counts["Total Erreurs"] = agence_error_counts[specific_error_columns].sum(axis=1)

        all_agences = df["Agence"].unique()
        agence_error_counts = pd.merge(
            pd.DataFrame({"Agence": all_agences}),
            agence_error_counts,
            on="Agence",
            how="left"
        ).fillna(0)

        total_errors_by_agence = agence_error_counts["Total Erreurs"].sum()
        agence_error_counts["Pourcentage"] = (agence_error_counts["Total Erreurs"] / total_errors_by_agence) * 100 if total_errors_by_agence > 0 else 0
        
        agence_error_counts = agence_error_counts.sort_values(by="Pourcentage", ascending=False).reset_index(drop=True)

        # Résultat des erreurs
        
        result = {
            "total_rows": total_rows,
            "rows_with_errors": rows_with_errors,
            "total_errors": total_errors,
            "error_summary": error_summary,
            "cc_error_counts": cc_error_counts.to_dict(orient="records"),
            "agence_error_counts": agence_error_counts.to_dict(orient="records"),
            "percentage_cc_with_errors": round((len(cc_error_counts[cc_error_counts["Total Erreurs"] > 0]) / len(all_cc)) * 100),
            "percentage_agences_with_errors": round((len(agence_error_counts[agence_error_counts["Total Erreurs"] > 0]) / len(all_agences)) * 100)
        }
        
        error_summary_df = pd.DataFrame(error_summary)  
        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, "erreurs_resume_latest.xlsx")
        error_summary_df.to_excel(file_path, index=False)



        # Générer un lien pour télécharger le fichier des erreurs
        download_link = "/download-invalid-file/"
        # Retourner un fichier Excel avec les lignes invalides en option
        return JSONResponse(content={
            "message": "Validation réussie",
            "download_link": download_link,
            "result": result  # Ajout des résultats détaillés
        })

        
    except Exception as e:
        return JSONResponse(content={"message": f"Erreur : {e}"}, status_code=500)

    finally:
        os.unlink(temp_file.name) 

@app.get("/download-invalid-file/")
async def download_invalid_file():
    try:
        # Définir le nom de fichier par défaut (généré au moment de la validation)
        temp_dir = os.path.join(os.getcwd(), "temp")  # Utilisez le même dossier ici aussi
        file_path = os.path.join(temp_dir, "erreurs_resume_latest.xlsx")



        # Vérification que le fichier a bien été créé
        if not os.path.isfile(file_path):
            print(f"Fichier non trouvé : {file_path}")
            return JSONResponse(content={"message": "Fichier d'erreur introuvable après validation."}, status_code=500)

        # Retourner le fichier pour le téléchargement
        return FileResponse(
            file_path, 
            filename="erreurs_resume_latest.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        
    except Exception as e:
        print(f"Erreur dans le téléchargement du fichier : {e}")
        return JSONResponse(content={"message": f"Erreur : {e}"}, status_code=500)
