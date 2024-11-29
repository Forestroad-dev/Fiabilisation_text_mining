<template>
    <div class="file-validator">
      <h2>Validation de fichier Excel</h2>
  
      <!-- Formulaire de téléchargement de fichier -->
      <input type="file" @change="handleFileUpload" />
      <button @click="submitFile" :disabled="!file">Valider</button>
  
      <!-- Afficher les résultats -->
      <div v-if="result">
        <h3>Résumé des erreurs :</h3>
        <ul>
          <li v-for="(count, category) in result.errors_by_category" :key="category">
            {{ category }} : {{ count }} erreurs
          </li>
        </ul>
        <p>Total des erreurs : {{ result.total_errors }}</p>
  
        <!-- Lien pour télécharger les fichiers générés -->
        <div v-if="result.invalid_rows_file">
          <a :href="result.invalid_rows_file" download="invalid_rows.xlsx">Télécharger les lignes invalides</a>
        </div>
  
        <!-- Affichage du graphique -->
        <div v-if="result.error_plot_file">
          <a :href="result.error_plot_file" download="error_plot.png">Télécharger le graphique des erreurs</a>
        </div>
      </div>
  
      <!-- Message d'erreur -->
      <div v-if="error" class="error-message">
        <p>{{ error }}</p>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        file: null,
        result: null,
        error: null,
      };
    },
    methods: {
      handleFileUpload(event) {
        this.file = event.target.files[0];
      },
      async submitFile() {
        if (!this.file) {
          this.error = "Veuillez sélectionner un fichier.";
          return;
        }
  
        const formData = new FormData();
        formData.append('file', this.file);
  
        try {
          // Envoyer le fichier à l'API FastAPI
          const response = await axios.post('http://127.0.0.1:8000/validate/', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });
  
          // Mettre à jour le résultat avec les données retournées
          this.result = response.data;
          this.error = null;
        } catch (err) {
          console.error(err);
          this.error = "Erreur lors de la validation du fichier. Veuillez réessayer.";
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .error-message {
    color: red;
  }
  </style>
  