<template>
  <div class="py-4 container-fluid">
    
    <div class="row">
      <div
        class="d-flex flex-column align-items-center justify-content-center"
        style="height: 20h; background-color: white; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); margin: 10px; border-radius: 8px; padding: 50px;"
      >
        <div class="mb-3 d-flex align-items-center" style="margin-top: 20px;">
          <h3>Saisir un fichier</h3>
          <div style="flex-grow: 1; margin-left: 10px;">
            <input type="file" id="file-upload" class="form-control" style="border: 2px solid red;" />
          </div>
          <span id="validation-icon" class="d-none" style="font-size: 20px; color: green; margin-left: 10px;">✔</span>
        </div>

        <button
          class="btn"
          id="upload-button"
          style="background: linear-gradient(310deg, #ad1717 0%, #ec2d2d 100%); color: white; border: none;"
        >
          Envoyer
        </button>
        <div id="spinner" class="d-none" style="font-size: 24px; color: red; margin-left: 10px;">
          <i class="fa fa-spinner fa-spin"></i> Chargement...
        </div>
      </div>
    </div>

    <div class="row d-flex justify-content-between">
      <!-- Affichage des statistiques -->
      <div class="col-xl-2.5 col-sm-6 mb-xl-0 mb-4">
        <mini-statistics-card
          title="Nombre de lignes"
          :value="totalRows"
          :percentage="{
            value: 'N/A',
            color: 'text-muted',
          }"
          :icon="{
            component: 'ni ni-books',
            background: iconBackground,
          }"
          style="background: linear-gradient(310deg, #ad1717 0%, #ec2d2d 100%); color: white;"
          :title-style="{ color: 'white' }"
          :value-style="{ color: 'white' }"
          :percentage-style="{ color: 'white' }"
          direction-reverse
        />
      </div>
    </div>
    <div class="row d-flex justify-content-between">
      <div class="col-xl-3 col-sm-6 mb-xl-0 mb-4">
        <mini-statistics-card
          title="lignes avec erreurs"
          :value="rowsWithErrors"
          :percentage="{
            value: 'N/A',
            color: 'text-danger',
          }"
          direction-reverse
        />
      </div>
      <div class="col-xl-3 col-sm-6 mb-xl-0 mb-4">
        <mini-statistics-card
          title="nombes d'erreurs"
          :value="totalErrors"
          :percentage="{
            value: 'N/A',
            color: 'text-danger',
          }"
          :icon="{
            component: 'ni ni-alert-circle-exc',
            background: iconBackground,
          }"
          direction-reverse
        />
      </div>
      <div class="col-xl-3 col-sm-6 mb-xl-0">
        <mini-statistics-card
          title="CC avec erreur"
          :value="`${percentage_cc_with_errors}%`"
          :percentage="{
            value: 'N/A',
            color: 'text-danger',
          }"
          :icon="{
            component: 'ni ni-alert-circle-exc',
            background: iconBackground,
          }"
          direction-reverse
        />
      </div>
      <div class="col-xl-3 col-sm-6 mb-xl-0 mb-4">
        <mini-statistics-card
          title="agence avec erreur"
          :value="`${percentage_agences_with_errors}%`"
          :percentage="{
            value: 'N/A',
            color: 'text-danger',
          }"
          :icon="{
            component: 'ni ni-alert-circle-exc',
            background: iconBackground,
          }"
          direction-reverse
        />
      </div>
    </div>

    <div class="row d-flex justify-content-between">
      <div
        v-for="(error, index) in errorSummary"
        :key="index"
        class="col-xl-3 col-sm-6 mb-xl-0 mb-4"
      >
        <mini-statistics-card
          :title="columnTitles[error.column] || error.column" 
          :value="error.count"
          :percentage="{
            value: 'N/A',
            color: 'text-danger',
          }"
          :icon="{
            component: 'ni ni-alert-circle-exc',
            background: iconBackground,
          }"
          direction-reverse
        />
      </div>
    </div>

    <div class="row">
      <div class="col-6">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Détails des Erreurs CC</h5>
            <!-- Conteneur pour le défilement -->
            <div style="max-height: 400px; overflow-y: auto;">
              <table class="table table-bordered">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>CC</th>
                    <th>Tél</th>
                    <th>Email</th>
                    <th>Sexe/Genre</th>
                    <th>Représentant</th>
                    <th>Total</th>
                    <th>Pourcentage</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(ccError, index) in ccErrorCounts" :key="ccError.CC">
                    <td>{{ index + 1 }}</td>
                    <td>{{ ccError.CC }}</td>
                    <td>{{ ccError['Format du Numéro de Téléphone Invalide'] }}</td>
                    <td>{{ ccError['Domaine ou Format de l\'Email Invalide'] }}</td>
                    <td>{{ ccError['Sexe ou Genre Incorrect ou Manquant pour Entreprise'] }}</td>
                    <td>{{ ccError['Représentant Légal Manquant'] }}</td>
                    <td :class="{ 'bg-secondary text-danger': ccError['Total Erreurs'] > 4 }">
                      {{ ccError['Total Erreurs'] }}
                    </td>
                    <td :class="{ 'bg-secondary text-danger': ccError.Pourcentage > 5 }">
                      {{ (ccError.Pourcentage).toFixed(2) }}%
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- Fin du conteneur -->
          </div>
        </div>
      </div>
    </div>

    <br>
    <hr style="border: 2px solid blue;">
    <br>
    
    <div class="row">
      <div class="col-6">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Détails des Erreurs Agence</h5>
            <!-- Conteneur avec défilement pour la table -->
            <div style="max-height: 400px; overflow-y: auto;">
              <table class="table table-bordered">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Agence</th>
                    <th>Tél</th>
                    <th>Email</th>
                    <th>Sexe/Genre</th>
                    <th>Représentant</th>
                    <th>Total</th>
                    <th>Pourcentage</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(agenceError, index) in agenceErrorCounts" :key="agenceError.agence">
                    <td>{{ index + 1 }}</td>
                    <td>{{ agenceError.Agence }}</td>
                    <td>{{ agenceError['Format du Numéro de Téléphone Invalide'] }}</td>
                    <td>{{ agenceError['Domaine ou Format de l\'Email Invalide'] }}</td>
                    <td>{{ agenceError['Sexe ou Genre Incorrect ou Manquant pour Entreprise'] }}</td>
                    <td>{{ agenceError['Représentant Légal Manquant'] }}</td>
                    <td :class="{ 'bg-secondary text-danger': agenceError['Total Erreurs'] > 4 }">
                      {{ agenceError['Total Erreurs'] }}
                    </td>
                    <td :class="{ 'bg-secondary text-danger': agenceError.Pourcentage > 5 }">
                      {{ (agenceError.Pourcentage).toFixed(2) }}%
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- Fin du conteneur -->
          </div>
        </div>
      </div>
    </div>

    
    <div class="mt-4 row">
      <div class="mb-4 col-lg-5 mb-lg-0">
        <div class="card z-index-2">
          <div class="p-3 card-body">
            <reports-bar-chart
              id="chart-bar"
              title="active Users"
              description="(<strong>+23%</strong>) than last week"
              :chart="{
                labels: [
                  'Apr',
                  'May',
                  'Jun',
                  'Jul',
                  'Aug',
                  'Sep',
                  'Oct',
                  'Nov',
                  'Dec',
                ],
                datasets: {
                  label: 'Sales',
                  data: [450, 200, 100, 220, 500, 100, 400, 230, 500],
                },
              }"
              :items="[
                {
                  icon: {
                    color: 'primary',
                    component: faUsers,
                  },
                  label: 'users',
                  progress: { content: '37K', percentage: 60 },
                },
                {
                  icon: { color: 'info', component: faHandPointer },
                  label: 'clicks',
                  progress: { content: '2m', percentage: 90 },
                },
                {
                  icon: { color: 'warning', component: faCreditCard },
                  label: 'Sales',
                  progress: { content: '435$', percentage: 30 },
                },
                {
                  icon: { color: 'danger', component: faScrewdriverWrench },
                  label: 'Items',
                  progress: { content: '43', percentage: 50 },
                },
              ]"
            />
          </div>
        </div>
      </div>
      <div class="col-lg-7">
        <!-- line chart -->
        <div class="card z-index-2">
          <gradient-line-chart
            id="chart-line"
            title="Gradient Line Chart"
            description="<i class='fa fa-arrow-up text-success'></i>
      <span class='font-weight-bold'>4% more</span> in 2021"
            :chart="{
              labels: [
                'Apr',
                'May',
                'Jun',
                'Jul',
                'Aug',
                'Sep',
                'Oct',
                'Nov',
                'Dec',
              ],
              datasets: [
                {
                  label: 'Mobile Apps',
                  data: [50, 40, 300, 220, 500, 250, 400, 230, 500],
                },
                {
                  label: 'Websites',
                  data: [30, 90, 40, 140, 290, 290, 340, 230, 400],
                },
              ],
            }"
          />
        </div>
      </div>
    </div>
    <div class="row my-4">
      <div class="col-lg-8 col-md-6 mb-md-0 mb-4">
        <!-- <projects-card /> -->
      </div>
      <div class="col-lg-4 col-md-6">
        <timeline-list
          class="h-100"
          title="Orders overview"
          description="<i class='fa fa-arrow-up text-success' aria-hidden='true'></i>
        <span class='font-weight-bold'>24%</span> this month"
        >
          <timeline-item
            color="success"
            icon="bell-55"
            title="$2400 Design changes"
            date-time="22 DEC 7:20 PM"
          />
          <TimelineItem
            color="danger"
            icon="html5"
            title="New order #1832412"
            date-time="21 DEC 11 PM"
          />
          <TimelineItem
            color="info"
            icon="cart"
            title="Server payments for April"
            date-time="21 DEC 9:34 PM"
          />
          <TimelineItem
            color="warning"
            icon="credit-card"
            title="New card added for order #4395133"
            date-time="20 DEC 2:20 AM"
          />
          <TimelineItem
            color="primary"
            icon="key-25"
            title="Unlock packages for development"
            date-time="18 DEC 4:54 AM"
          />
          <TimelineItem
            color="info"
            icon="check-bold"
            title="Notifications unread"
            date-time="15 DEC"
          />
        </timeline-list>
      </div>
    </div>
  </div>
</template>
<script>

import MiniStatisticsCard from "@/examples/Cards/MiniStatisticsCard.vue";
import ReportsBarChart from "@/examples/Charts/ReportsBarChart.vue";
import GradientLineChart from "@/examples/Charts/GradientLineChart.vue";
import TimelineList from "./components/TimelineList.vue";
import TimelineItem from "./components/TimelineItem.vue";
// import ProjectsCard from "./components/ProjectsCard.vue";
export default {
  components: {
    MiniStatisticsCard,
    ReportsBarChart,
    GradientLineChart,
    // ProjectsCard,
    TimelineList,
    TimelineItem,
  },

  data() {
    return {
      totalRows: 0,
      rowsWithErrors: 0,
      totalErrors: 0,
      errorSummary: [],
      columnTitles: {
        "Format du Numéro de Téléphone Invalide": "Téléphone Invalide",
        "Domaine ou Format de l'Email Invalide": "Email Invalide",
        "Sexe ou Genre Incorrect ou Manquant pour Entreprise": "Sexe/Genre",
        "Représentant Légal Manquant": "Représentant ",
      },
      ccErrorCounts: [],
      agenceErrorCounts: [],
      iconBackground: '#5E72E4',
      percentage_cc_with_errors : 0,
      percentage_agences_with_errors : 0,
      

    };
  },

  methods: {
    async uploadFile() {
  const fileInput = document.getElementById('file-upload');
  const validationIcon = document.getElementById('validation-icon');
  
  // Ajout d'une classe de bordure verte et fond de couleur pour indiquer la sélection du fichier
  fileInput.style.border = "2px solid green";
  fileInput.style.backgroundColor = "#d4edda";
  
  const file = fileInput.files[0];

  if (!file) {
    alert("Veuillez sélectionner un fichier.");
    return;
  }

  // Affichage du spinner et désactivation du bouton d'upload
  document.getElementById("spinner").classList.remove("d-none");
  document.getElementById("file-upload").disabled = true;

  const formData = new FormData();
  formData.append("file", file);

  try {
    // Envoi du fichier vers l'API
    const response = await fetch('http://localhost:8000/validate-excel/', {
      method: 'POST',
      body: formData,
    });

    const result = await response.json();

    // Masquer le spinner et réactiver l'input
    document.getElementById("spinner").classList.add("d-none");
    document.getElementById("file-upload").disabled = false;

    if (response.ok) {
      // Affichage de l'icône de validation en cas de succès
      validationIcon.classList.remove("d-none"); // Affiche l'icône de validation
      validationIcon.style.color = "green"; // Change la couleur de l'icône en vert
      this.updateStats(result.result); // Mise à jour des stats ou résultats
    } else {
      // Masquer l'icône et indiquer l'échec si nécessaire
      validationIcon.classList.add("d-none");
      console.error(`Erreur : ${result.message}`);
    }
  } catch (error) {
    // Si une erreur se produit lors de la requête, afficher un message d'erreur
    console.error('Erreur:', error);
    validationIcon.classList.add("d-none"); // Masquer l'icône si une erreur se produit
    alert("Une erreur est survenue lors de l'envoi du fichier.");

    // Masquer le spinner et réactiver le bouton
    document.getElementById("spinner").classList.add("d-none");
    document.getElementById("file-upload").disabled = false;
  }
}

,

    updateStats(result) {
      this.totalRows = result.total_rows;
      this.rowsWithErrors = result.rows_with_errors;
      this.totalErrors = result.total_errors;
      this.errorSummary = result.error_summary;
      this.ccErrorCounts = result.cc_error_counts.map((item) => ({
        ...item,
        Pourcentage: item.Pourcentage || 0, // Par défaut à 0 si non fourni
      }));
      this.agenceErrorCounts = result.agence_error_counts || [];
      this.percentage_cc_with_errors = result.percentage_cc_with_errors;
      this.percentage_agences_with_errors = result.percentage_agences_with_errors;
    },

  },

  mounted() {
    document.getElementById('upload-button').addEventListener('click', this.uploadFile);
  },
};
</script>
