from fastapi import FastAPI, UploadFile, HTTPException
import pandas as pd
import re
from io import BytesIO

# Créer l'application FastAPI
app = FastAPI()

# Endpoint pour valider un fichier Excel
@app.post("/validate-excel/")
async def validate_excel(file: UploadFile):
    if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        raise HTTPException(status_code=400, detail="Le fichier doit être un fichier Excel (.xlsx)")
    
    # Charger le fichier Excel
    try:
        df = pd.read_excel(BytesIO(await file.read()))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Erreur lors de la lecture du fichier Excel.")
    
    # Appliquez ici la logique de votre fonction `validate_excel`
    invalid_rows = []
    for idx, row in df.iterrows():
        errors = {"Matricule Client": row.get("Matricule Client", "Inconnu")}
        
        # Validation du téléphone (exemple simplifié)
        phone = re.sub(r"\D", "", str(row.get("Telephone Client", "")))
        if not phone or len(phone) != 9:
            errors["Format du Numéro de Téléphone Invalide"] = "Numéro invalide."
        
        # Ajouter les erreurs au tableau si nécessaire
        if len(errors) > 1:
            invalid_rows.append(errors)
    
    # Retourner les lignes invalides ou un message de succès
    if invalid_rows:
        return {"status": "error", "invalid_rows": invalid_rows}
    return {"status": "success", "message": "Toutes les lignes sont valides."}
