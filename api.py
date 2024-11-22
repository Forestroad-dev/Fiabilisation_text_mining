from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
from io import BytesIO
from fiabilisation import validate_excel  # Assurez-vous que cette fonction est bien définie

app = FastAPI()

@app.post("/validate-excel/")
async def validate_excel_file(file: UploadFile = File(...)):
    # Lire le fichier Excel téléchargé
    try:
        df = pd.read_excel(file.file)
    except Exception as e:
        return JSONResponse(content={"message": f"Erreur lors de la lecture du fichier : {e}"}, status_code=400)

    # Spécifier le chemin de sortie pour enregistrer les erreurs
    output_path = "/tmp/invalid_rows.xlsx"

    # Exécuter la validation
    try:
        invalid_data = validate_excel(file.file, output_path)
    except Exception as e:
        return JSONResponse(content={"message": f"Erreur lors de la validation : {e}"}, status_code=400)

    total_errors = 0
    error_counts = invalid_data.apply(lambda x: x != "").sum()
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

    # Résultat des erreurs
    result = {
        "total_errors": total_errors,
        "error_summary": error_summary,
        "cc_error_counts": cc_error_counts.to_dict(orient="records"),
        "agence_error_counts": agence_error_counts.to_dict(orient="records"),
        "percentage_cc_with_errors": (len(cc_error_counts[cc_error_counts["Total Erreurs"] > 0]) / len(all_cc)) * 100,
        "percentage_agences_with_errors": (len(agence_error_counts[agence_error_counts["Total Erreurs"] > 0]) / len(all_agences)) * 100
    }

    # Retourner un fichier Excel avec les lignes invalides en option
    return JSONResponse(content=result)

@app.get("/download-invalid-file/")
async def download_invalid_file():
    return FileResponse("/tmp/invalid_rows.xlsx", filename="invalid_rows.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
