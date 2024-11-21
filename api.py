from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fiabilisation import validate_excel  

app = FastAPI()

@app.get("/")
async def home():
    return {"message": "Bienvenue sur l'API de validation des comptes client"}


# Route pour l'upload du fichier
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Lire le fichier Excel
        df = pd.read_excel(file.file)
        return {"message": f"Fichier chargé avec {df.shape[0]} lignes", "data_preview": df.head().to_html()}
    except Exception as e:
        return {"error": f"Erreur lors de la lecture du fichier : {e}"}

# Route pour traiter et valider les données
@app.post("/validate/")
async def validate_and_generate(file: UploadFile = File(...)):
    try:
        # Charger et valider les données
        df = pd.read_excel(file.file)
        output_path = "invalid_rows.xlsx"
        invalid_data = validate_excel(file.file, output_path)
        
        # Calculer les erreurs
        error_counts = invalid_data.apply(lambda x: x != "").sum()
        filtered_errors = {column: count for column, count in error_counts.items()
                           if count > 0 and column not in ["Matricule Client", "Nom Client", "Agence", "N° Compte", "CC"]}
        
        # Créer un graphique
        fig, ax = plt.subplots()
        categories = list(filtered_errors.keys())
        counts = list(filtered_errors.values())
        ax.bar(categories, counts, color='skyblue')
        ax.set_title("Nombre d'erreurs par catégorie")
        ax.set_xlabel("Catégorie")
        ax.set_ylabel("Nombre d'erreurs")
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha="right")
        
        # Sauvegarder le graphique en mémoire et retourner le fichier image
        img_io = BytesIO()
        plt.savefig(img_io, format='png')
        img_io.seek(0)
        
        # Renvoi du graphique au format image
        return HTMLResponse(content=f'<img src="data:image/png;base64,{img_io.getvalue().encode("base64")}" />')
    
    except Exception as e:
        return {"error": f"Erreur lors de la validation : {e}"}

# Route pour télécharger le fichier d'erreurs
@app.get("/download/")
async def download_file():
    try:
        return FileResponse("invalid_rows.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="invalid_rows.xlsx")
    except Exception as e:
        return {"error": f"Erreur lors du téléchargement du fichier : {e}"}
