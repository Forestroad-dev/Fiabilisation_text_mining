<template>
  <div class="py-4 container-fluid">
    <div class="row">
      <div
        class="d-flex flex-column align-items-center justify-content-center"
        style="
          height: 20h;
          background-color: white;
          box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
          margin: 10px;
          border-radius: 8px;
          padding: 50px;
        "
      >
        <div class="mb-3 d-flex align-items-center" style="margin-top: 20px">
          <h3>Saisir un fichier</h3>
          <div style="flex-grow: 1; margin-left: 10px">
            <input
              type="file"
              id="file-upload"
              class="form-control"
              style="border: 2px solid red"
            />
          </div>
          <span
            id="validation-icon"
            class="d-none"
            style="font-size: 20px; color: green; margin-left: 10px"
            >✔</span
          >
        </div>

        <button
          class="btn"
          id="upload-button"
          style="
            background: linear-gradient(310deg, #ad1717 0%, #ec2d2d 100%);
            color: white;
            border: none;
          "
        >
          Valider
        </button>

        <button
          v-if="isValidationComplete"
          @click="downloadInvalidFile"
          class="btn btn-primary mt-3"
          style="
            background: linear-gradient(310deg, #ad1717 0%, #ec2d2d 100%);
            color: white;
            border: none;
          "
        >
          <i class="fas fa-download"></i>
          <!-- Icône de téléchargement -->
        </button>

        <div
          id="spinner"
          class="d-none"
          style="font-size: 24px; color: red; margin-left: 10px"
        >
          <i class="fa fa-spinner fa-spin"></i> Chargement...
        </div>
      </div>
    </div>

    <div class="row d-flex justify-content-between">
      <!-- Affichage des statistiques -->
      <div class="col-xl-2.5 col-sm-6 mb-xl-0 mb-4">
        <mini-statistics-card
          title="Nombre de comptes"
          :value="totalRows"
          :percentage="{
            value: 'N/A',
            color: 'text-muted',
          }"
          style="
            background: linear-gradient(310deg, #ad1717 0%, #ec2d2d 100%);
            color: white;
          "
          :title-style="{ color: 'gray', fontWeight: 'bold' }"
          :value-style="{ color: 'white' }"
          :percentage-style="{ color: 'white' }"
          direction-reverse
        />
      </div>
      <div class="col-xl-2.5 col-sm-6 mb-xl-0 mb-4">
        <mini-statistics-card
          title="Nom du fichier"
          :value="fileName || 'Aucun fichier chargé'"
          :percentage="{
            value: 'N/A',
            color: 'text-muted',
          }"
          style="
            background: linear-gradient(310deg, #ad1717 0%, #ec2d2d 100%);
            color: white;
          "
          :title-style="{ color: 'white' }"
          :value-style="{ color: 'white' }"
          :percentage-style="{ color: 'white' }"
          direction-reverse
          class="custom-value-card"
        />
      </div>
      <div>
        <button
          v-if="isValidationComplete"
          @click="downloadInvalidFile"
          class="btn btn-primary mt-3"
          style="
            background: linear-gradient(310deg, #ad1717 0%, #ec2d2d 100%);
            color: black;
            border: none;
          "
        >
          Télécharger les données invalides
        </button>
      </div>
    </div>
    <div class="row d-flex justify-content-between">
      <div class="col-xl-3 col-sm-6 mb-xl-0 mb-4">
        <mini-statistics-card
          title="Nombre de compte avec erreurs "
          :value="rowsWithErrors"
          :percentage="{
            value: 'N/A',
            color: 'text-danger',
          }"
          style="background-color: white; color: #ec2d2d"
          direction-reverse
        />
      </div>
      <div class="col-xl-3 col-sm-6 mb-xl-0 mb-4">
        <mini-statistics-card
          title="Nombres total d'erreurs comptes"
          :value="totalErrors"
          :percentage="{
            value: 'N/A',
            color: 'text-danger',
          }"
          :icon="{
            component: 'ni ni-alert-circle-exc',
            background: iconBackground,
          }"
          style="background-color: white; color: #ec2d2d"
          direction-reverse
        />
      </div>
      <div class="col-xl-3 col-sm-6 mb-xl-0">
        <mini-statistics-card
          title="Pourcentage de CC ayant des erreurs "
          :value="`${percentage_cc_with_errors}%`"
          :percentage="{
            value: 'N/A',
            color: 'text-danger',
          }"
          :icon="{
            component: 'ni ni-alert-circle-exc',
            background: iconBackground,
          }"
          style="background-color: white; color: #ec2d2d"
          direction-reverse
        />
      </div>
      <div class="col-xl-3 col-sm-6 mb-xl-0 mb-4">
        <mini-statistics-card
          title="Pourcentage d'agences ayant des erreurs"
          :value="`${percentage_agences_with_errors}%`"
          :percentage="{
            value: 'N/A',
            color: 'text-danger',
          }"
          :icon="{
            component: 'ni ni-alert-circle-exc',
            background: iconBackground,
          }"
          style="background-color: white; color: #ec2d2d"
          direction-reverse
        />
      </div>
    </div>

    <br />
    <h5>Types d'erreurs</h5>
    <hr style="border: 2px solid gray" />
    <br />

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
          style="
            background: linear-gradient(310deg, #ad1717 0%, #ec2d2d 100%);
            color: white;
          "
          direction-reverse
        />
      </div>
    </div>

    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Détails des Erreurs commises par les CC</h5>
            <!-- Filtre CC -->
            <div class="mb-3">
              <label for="filterCC" class="form-label">Filtrer par CC :</label>
              <select
                id="filterCC"
                v-model="selectedCC"
                class="form-select"
                style="font-family: 'Arial', sans-serif; font-size: 14px"
              >
                <option value="">Tous les CC</option>
                <option
                  v-for="cc in uniqueCCs"
                  :key="cc"
                  :value="cc"
                  style="font-family: 'Arial', sans-serif; font-size: 14px"
                >
                  {{ cc }}
                </option>
              </select>
            </div>
            <button
              @click="exportTableToExcel"
              class="btn btn-success"
              style="
                background: linear-gradient(310deg, #4caf50 0%, #2e7d32 100%);
                color: white;
                border: none;
              "
            >
              <i class="fas fa-file-excel"></i> Exporter en Excel
            </button>
            <!-- Conteneur pour le défilement -->
            <div style="max-height: 400px; overflow-y: auto">
              <table
                class="table table-bordered"
                style="border: 1px solid black; border-collapse: collapse"
              >
                <thead
                  style="
                    position: sticky;
                    top: 0;
                    background: linear-gradient(
                      310deg,
                      #ad1717 0%,
                      #ec2d2d 100%
                    );
                    color: white;
                    z-index: 2;
                  "
                >
                  <tr>
                    <th>ID</th>
                    <th>CC</th>
                    <th>Tél</th>
                    <th>Email</th>
                    <th>Sexe/Genre</th>
                    <th>Représentant</th>
                    <th>Agence</th>
                    <th>Total Erreurs Agence</th>
                    <th>Taux d'Erreurs du CC dans l'Agence</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(ccError, index) in filteredErrors"
                    :key="generateUniqueId(index, ccError.CC)"
                    :class="{ 'text-danger': ccError.Pourcentage > 1 }"
                  >
                    <td>{{ index + 1 }}</td>
                    <td>{{ ccError.CC }}</td>
                    <td>
                      {{ ccError["Format du Numéro de Téléphone Invalide"] }}
                    </td>
                    <td>
                      {{ ccError["Domaine ou Format de l'Email Invalide"] }}
                    </td>
                    <td>
                      {{
                        ccError[
                          "Sexe ou Genre Incorrect ou Manquant pour Entreprise"
                        ]
                      }}
                    </td>
                    <td>{{ ccError["Représentant Légal Manquant"] }}</td>
                    <td>{{ ccError.Agence }}</td>
                    <td>{{ ccError["Total Erreurs Agence"] }}</td>
                    <td>{{ ccError["Pourcentage Par Agence"].toFixed(2) }}%</td>
                  </tr>
                  <!-- Ligne Total -->
                  <tr
                    style="
                      background: linear-gradient(
                        310deg,
                        #ad1717 0%,
                        #ec2d2d 100%
                      );
                      color: white;
                      font-weight: bold;
                    "
                  >
                    <td colspan="2">Total</td>
                    <td>{{ totalTel }}</td>
                    <td>{{ totalEmail }}</td>
                    <td>{{ totalSexeGenre }}</td>
                    <td>{{ totalRepresentant }}</td>
                    <td>—</td>
                    <td>{{ totalErreursAgence }}</td>
                    <td>
                      {{
                        totalPourcentageAgence > 100
                          ? 100
                          : totalPourcentageAgence
                      }}%
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

    <br />
    <hr style="border: 2px solid gray" />
    <br />

    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">
              Détails des Erreurs commises par les agences
            </h5>

            <!-- Filtrer par Agence -->
            <div class="mb-3">
              <label for="filterAgence" class="form-label"
                >Filtrer par Agence :</label
              >
              <select
                id="filterAgence"
                v-model="selectedAgence"
                class="form-select"
                style="font-family: 'Arial', sans-serif; font-size: 14px"
              >
                <option value="">Toutes les Agences</option>
                <option
                  v-for="agence in uniqueAgences"
                  :key="agence"
                  :value="agence"
                  style="font-family: 'Arial', sans-serif; font-size: 14px"
                >
                  {{ agence }}
                </option>
              </select>
            </div>

            <button
              @click="exportAgenceTableToExcel"
              class="btn btn-success"
              style="
                background: linear-gradient(310deg, #4caf50 0%, #2e7d32 100%);
                color: white;
                border: none;
              "
            >
              <i class="fas fa-file-excel"></i> Exporter en Excel
            </button>

            <!-- Conteneur avec défilement pour la table -->
            <div style="max-height: 400px; overflow-y: auto">
              <table
                class="table table-bordered"
                style="border: 1px solid black; border-collapse: collapse"
              >
                <thead
                  style="
                    position: sticky;
                    top: 0;
                    background: linear-gradient(
                      310deg,
                      #ad1717 0%,
                      #ec2d2d 100%
                    );
                    color: white;
                    z-index: 2;
                  "
                >
                  <tr>
                    <th>ID</th>
                    <th>Agence</th>
                    <th>Tél</th>
                    <th>Email</th>
                    <th>Sexe/Genre</th>
                    <th>Représentant</th>
                    <th>Nombre de CC</th>
                    <th>Total</th>
                    <th>Pourcentage</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(agenceError, index) in filteredAgenceErrors"
                    :key="agenceError.Agence"
                    :class="{ 'text-danger': agenceError.Pourcentage > 1 }"
                  >
                    <td>{{ index + 1 }}</td>
                    <td>{{ agenceError.Agence }}</td>
                    <td>
                      {{
                        agenceError["Format du Numéro de Téléphone Invalide"]
                      }}
                    </td>
                    <td>
                      {{ agenceError["Domaine ou Format de l'Email Invalide"] }}
                    </td>
                    <td>
                      {{
                        agenceError[
                          "Sexe ou Genre Incorrect ou Manquant pour Entreprise"
                        ]
                      }}
                    </td>
                    <td>{{ agenceError["Représentant Légal Manquant"] }}</td>
                    <td>{{ agenceError["Nombre de CC"] }}</td>
                    <td>
                      {{ agenceError["Total Erreurs"] }}
                    </td>
                    <td>{{ agenceError.Pourcentage.toFixed(2) }}%</td>
                  </tr>
                  <tr
                    style="
                      background: linear-gradient(
                        310deg,
                        #ad1717 0%,
                        #ec2d2d 100%
                      );
                      color: white;
                      font-weight: bold;
                    "
                  >
                    <td colspan="2">Totaux</td>
                    <td>
                      {{
                        calculateTotal(
                          "Format du Numéro de Téléphone Invalide",
                          "agence"
                        )
                      }}
                    </td>
                    <td>
                      {{
                        calculateTotal(
                          "Domaine ou Format de l'Email Invalide",
                          "agence"
                        )
                      }}
                    </td>
                    <td>
                      {{
                        calculateTotal(
                          "Sexe ou Genre Incorrect ou Manquant pour Entreprise",
                          "agence"
                        )
                      }}
                    </td>
                    <td>
                      {{
                        calculateTotal("Représentant Légal Manquant", "agence")
                      }}
                    </td>
                    <td>{{ calculateTotal("Nombre de CC", "agence") }}</td>
                    <td>{{ calculateTotal("Total Erreurs", "agence") }}</td>
                    <td>
                      {{
                        calculatePercentageTotal(
                          "Pourcentage",
                          "agence"
                        ).toFixed(2)
                      }}%
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
      <div class="mb-6 col-lg-12">
        <div class="card z-index-2">
          <div class="p-3 card-body">
            <!-- Replace the reports-bar-chart with a canvas -->
            <canvas id="agenceChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>

      <!-- Diagramme circulaire du pourcentage d'erreur par CC -->
      <div class="col-lg-6 col-md-6 mb-4">
        <div class="card z-index-2">
          <div class="card-body">
            <h5 class="card-title">Pourcentage d'Erreur par CC</h5>
            <canvas id="ccErrorChart" width="400" height="400"></canvas>
          </div>
        </div>
      </div>

      <!-- Diagramme circulaire du pourcentage de CC avec erreurs -->
      <div class="col-lg-6 col-md-6 mb-4">
        <div class="card z-index-2">
          <div class="card-body">
            <h5 class="card-title">Pourcentage de CC ayant des erreurs</h5>
            <canvas id="ccWithErrorChart" width="400" height="400"></canvas>
          </div>
        </div>
      </div>

      <div class="col-lg-6 col-md-6 mb-4">
        <timeline-list
          class="h-100"
          title="Classement des CC ayant commis le plus d'erreurs"
          :description="`<span class='icon-left' style='font-size: 1.5em; vertical-align: middle; ><span v-if='showIcon'>🔻</span> Les hauts totaux d'erreurs</span>`"
          :showIcon="true"
        >
          <timeline-item
            v-for="(cc, index) in ccPodium"
            :key="index"
            :color="getPodiumColor(index)"
            :icon="`${
              index === 0
                ? 'fa fa-star'
                : index === 1
                ? 'fa fa-star-half-alt'
                : index === 2
                ? 'fa fa-star-of-david'
                : 'fa fa-star-o'
            }`"
            :title="`${cc.CC} (${cc['Total Erreurs']} erreurs)`"
            :date-time="`Pourcentage: ${cc.Pourcentage.toFixed(2)}%`"
            :style="{ fontSize: '1.5em' }"
          />
        </timeline-list>
      </div>
      <div class="col-lg-6 col-md-6 mb-4">
        <div class="card z-index-2">
          <div class="card-body">
            <h5 class="card-title">Pourcentage d'Agence ayant des erreurs</h5>
            <canvas id="agenceWithErrorChart" width="400" height="400"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import Chart from "chart.js/auto";
import * as XLSX from "xlsx";
import MiniStatisticsCard from "@/examples/Cards/MiniStatisticsCard.vue";
// import ReportsBarChart from "@/examples/Charts/ReportsBarChart.vue";
import TimelineList from "./components/TimelineList.vue";
import TimelineItem from "./components/TimelineItem.vue";
// import ProjectsCard from "./components/ProjectsCard.vue";
export default {
  components: {
    MiniStatisticsCard,
    // ReportsBarChart,
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
      iconBackground: "#5E72E4",
      percentage_cc_with_errors: 0,
      percentage_agences_with_errors: 0,
      agenceLabels: [], // Labels pour le graphique
      agenceTotals: [],
      ccPodium: [],
      fileName: "",
      downloadLink: "",
      isValidationComplete: false,
      selectedCC: "",
      selectedAgence: "",
    };
  },

  methods: {
    createChart() {
      if (this.chartInstance) {
        this.chartInstance.destroy();
      }
      if (this.ccErrorChart) {
        this.ccErrorChart.destroy();
      }
      if (this.ccWithErrorChart) {
        this.ccWithErrorChart.destroy();
      }
      if (this.agenceWithErrorChart) {
        this.agenceWithErrorChart.destroy();
      }

      // Crée le graphique des erreurs par agence
      console.log("Creating chart with data:", this.agenceErrorCounts);
      const agenceChartCtx = document
        .getElementById("agenceChart")
        .getContext("2d");
      const labels = this.agenceErrorCounts.map((agence) => agence.Agence);
      const data = this.agenceErrorCounts.map(
        (agence) => agence["Total Erreurs"]
      );

      if (this.chartInstance) {
        this.chartInstance.destroy();
      }

      this.chartInstance = new Chart(agenceChartCtx, {
        type: "bar",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Total Erreurs par Agence",
              data: data,
              backgroundColor: "#ec2d2d" /* Rouge sombre */,
              borderColor: "#8a1c1c" /* Rouge légèrement plus clair */,

              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      });

      // Crée le graphique circulaire pour le pourcentage d'erreur par CC
      const ccErrorChartCtx = document
        .getElementById("ccErrorChart")
        .getContext("2d");
      const ccErrorData = this.ccErrorCounts.map((cc) => cc.Pourcentage);
      const ccErrorLabels = this.ccErrorCounts.map((cc) => cc.CC);

      this.ccErrorChart = new Chart(ccErrorChartCtx, {
        type: "pie",
        data: {
          labels: ccErrorLabels,
          datasets: [
            {
              data: ccErrorData,
              backgroundColor: ccErrorData.map(() => this.getRandomColor()), // Génère des couleurs aléatoires
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            tooltip: {
              callbacks: {
                label: function (tooltipItem) {
                  return `${tooltipItem.label}: ${tooltipItem.raw.toFixed(2)}%`;
                },
              },
            },
          },
        },
      });

      // Crée le graphique circulaire pour le pourcentage de CC avec erreurs
      const ccWithErrorChartCtx = document
        .getElementById("ccWithErrorChart")
        .getContext("2d");
      const ccWithErrorCount = this.ccErrorCounts.filter(
        (cc) => cc.Pourcentage > 0
      ).length;
      const ccTotalCount = this.ccErrorCounts.length;
      const ccWithErrorPercentage = (ccWithErrorCount / ccTotalCount) * 100;
      const ccWithoutErrorPercentage = 100 - ccWithErrorPercentage;

      this.ccWithErrorChart = new Chart(ccWithErrorChartCtx, {
        type: "pie",
        data: {
          labels: ["CC avec erreurs", "CC sans erreurs"],
          datasets: [
            {
              data: [ccWithErrorPercentage, ccWithoutErrorPercentage],
              backgroundColor: ["#FF5733", "#d9d9d9"],
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            tooltip: {
              callbacks: {
                label: function (tooltipItem) {
                  return `${tooltipItem.label}: ${tooltipItem.raw.toFixed(2)}%`;
                },
              },
            },
          },
        },
      });

      // Crée le graphique circulaire pour le pourcentage d'agence avec erreurs
      const agenceWithErrorChartCtx = document
        .getElementById("agenceWithErrorChart")
        .getContext("2d");
      const agenceWithErrorCount = this.agenceErrorCounts.filter(
        (agence) => agence["Pourcentage"] > 0
      ).length;
      const agenceTotalCount = this.agenceErrorCounts.length;
      const agenceWithErrorPercentage =
        (agenceWithErrorCount / agenceTotalCount) * 100;
      const agenceWithoutErrorPercentage = 100 - agenceWithErrorPercentage;

      this.agenceWithErrorChart = new Chart(agenceWithErrorChartCtx, {
        type: "pie",
        data: {
          labels: ["Agence avec erreurs", "Agence sans erreurs"],
          datasets: [
            {
              data: [agenceWithErrorPercentage, agenceWithoutErrorPercentage],
              backgroundColor: ["#FF5733", "#d9d9d9"],
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            tooltip: {
              callbacks: {
                label: function (tooltipItem) {
                  return `${tooltipItem.label}: ${tooltipItem.raw.toFixed(2)}%`;
                },
              },
            },
          },
        },
      });
    },

    getRandomColor() {
      const letters = "0123456789ABCDEF";
      let color = "#";
      for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
      }
      return color;
    },

    getPodiumColor(index) {
      if (index === 0) return "gold";
      if (index === 1) return "silver";
      if (index === 2) return "bronze";
      return "secondary";
    },

    generateUniqueId(index, base = "") {
      return `${base}-${index}-${Math.random().toString(36).substr(2, 9)}`;
    },

    async uploadFile() {
      const fileInput = document.getElementById("file-upload");
      const validationIcon = document.getElementById("validation-icon");

      // Ajout d'une classe de bordure verte et fond de couleur pour indiquer la sélection du fichier
      fileInput.style.border = "2px solid green";
      fileInput.style.backgroundColor = "#d4edda";

      const file = fileInput.files[0];

      if (!file) {
        alert("Veuillez sélectionner un fichier.");
        return;
      }

      this.fileName = file.name;

      // Affichage du spinner et désactivation du bouton d'upload
      document.getElementById("spinner").classList.remove("d-none");
      document.getElementById("file-upload").disabled = true;

      const formData = new FormData();
      formData.append("file", file);

      try {
        // Envoi du fichier vers l'API
        const response = await fetch("http://localhost:8000/validate-excel/", {
          method: "POST",
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
          this.downloadLink = result.result.download_link;
          this.isValidationComplete = true;
        } else {
          // Masquer l'icône et indiquer l'échec si nécessaire
          validationIcon.classList.add("d-none");
          console.error(`Erreur : ${result.message}`);
        }
      } catch (error) {
        // Si une erreur se produit lors de la requête, afficher un message d'erreur
        console.error("Erreur:", error);
        validationIcon.classList.add("d-none"); // Masquer l'icône si une erreur se produit
        alert("Une erreur est survenue lors de l'envoi du fichier.");

        // Masquer le spinner et réactiver le bouton
        document.getElementById("spinner").classList.add("d-none");
        document.getElementById("file-upload").disabled = false;
      }
    },

    updateStats(result) {
      this.totalRows = result.total_rows;
      this.rowsWithErrors = result.rows_with_errors;
      this.totalErrors = result.total_errors;
      this.errorSummary = result.error_summary;
      // this.ccErrorCounts = result.cc_error_counts.map((item) => ({
      //   ...item,
      //   Pourcentage: item.Pourcentage || 0, // Par défaut à 0 si non fourni
      // }));

      this.ccErrorCounts = result.cc_error_counts.map((item) => ({
        ...item,
        Pourcentage: item.Pourcentage || 0, // Par défaut à 0 si non fourni
      }));
      // .filter((item) => item['Total Erreurs'] > 0) // Filtrer ceux avec un total supérieur à 0

      this.agenceErrorCounts = result.agence_error_counts || [];
      this.agenceLabels = this.agenceErrorCounts.map((item) => item.Agence);
      this.agenceTotals = this.agenceErrorCounts.map(
        (item) => item["Total Erreurs"]
      );

      console.log("agenceLabels:", this.agenceLabels);
      console.log("agenceTotals:", this.agenceTotals);

      this.percentage_cc_with_errors = result.percentage_cc_with_errors;
      this.percentage_agences_with_errors =
        result.percentage_agences_with_errors;
      this.ccPodium = Array.from(
        new Map(
          result.cc_error_counts
            .filter((cc) => cc.Pourcentage > 5) // Filtrer les CC avec un pourcentage > 5%
            .sort((a, b) => b["Total Erreurs"] - a["Total Erreurs"]) // Trier par 'Total Erreurs'
            .map((cc) => [cc.CC, cc]) // Utiliser le champ 'CC' comme clé pour garantir l'unicité
        ).values()
      );

      const labels = [...this.agenceLabels];
      const totals = [...this.agenceTotals];

      console.log("Labels normaux :", labels);
      console.log("Données normales :", totals);

      if (
        !result.agence_error_counts ||
        result.agence_error_counts.length === 0
      ) {
        console.error("Aucune donnée trouvée pour les erreurs par agence.");
        return;
      }
      this.createChart();
    },

    async downloadInvalidFile() {
      try {
        const response = await fetch(
          "http://localhost:8000/download-invalid-file/",
          {
            method: "GET",
          }
        );

        if (response.ok) {
          const blob = await response.blob();
          const downloadUrl = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = downloadUrl;

          // Utilisation du nom du fichier par défaut (invalid_data suivi de fileName)
          const defaultFileName = `invalid_data_${
            this.fileName || "default"
          }.xlsx`;

          a.download = defaultFileName; // Nom dynamique basé sur le fileName ou "default"
          document.body.appendChild(a);
          a.click();
          a.remove();
          window.URL.revokeObjectURL(downloadUrl); // Libération de l'URL
        } else {
          const result = await response.json();
          alert(result.message || "Erreur lors du téléchargement du fichier.");
        }
      } catch (error) {
        console.error("Erreur lors du téléchargement :", error);
        alert("Une erreur est survenue lors du téléchargement du fichier.");
      }
    },
    exportTableToExcel() {
      // Transformez les données pour sélectionner ou renommer les colonnes spécifiques
      const data = this.ccErrorCounts.map((item, index) => ({
        ID: index + 1,
        CC: item.CC,
        Tél: item["Format du Numéro de Téléphone Invalide"],
        Email: item["Domaine ou Format de l'Email Invalide"],
        "Sexe/Genre":
          item["Sexe ou Genre Incorrect ou Manquant pour Entreprise"],
        Représentant: item["Représentant Légal Manquant"],
        Agence: item.Agence,
        "Total Erreurs Agence": item["Total Erreurs Agence"],
        "Pourcentage par Agence":
          item["Pourcentage Par Agence"].toFixed(2) + " %", // Assurez-vous que ce nom est unique
      }));

      // Crée une nouvelle feuille Excel avec des colonnes bien définies
      const worksheet = XLSX.utils.json_to_sheet(data);

      // Ajoute des titres de colonnes (facultatif)
      const columns = [
        "ID",
        "CC",
        "Tél",
        "Email",
        "Sexe/Genre",
        "Représentant",
        "Agence",
        "Total Erreurs Agence",
        "Pourcentage par Agence",
      ];
      XLSX.utils.sheet_add_aoa(worksheet, [columns], { origin: "A1" });

      // Crée un classeur Excel
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, "Détails des Erreurs");

      // Génère et télécharge le fichier Excel
      const fileName = "erreurs_cc.xlsx";
      XLSX.writeFile(workbook, fileName);
    },

    exportAgenceTableToExcel() {
      // Préparation des données du tableau
      const data = this.agenceErrorCounts.map((item, index) => ({
        ID: index + 1,
        Agence: item.Agence,
        Tél: item["Format du Numéro de Téléphone Invalide"],
        Email: item["Domaine ou Format de l'Email Invalide"],
        "Sexe/Genre":
          item["Sexe ou Genre Incorrect ou Manquant pour Entreprise"],
        Représentant: item["Représentant Légal Manquant"],
        "Nombre de CC": item["Nombre de CC"],
        "Total Erreurs": item["Total Erreurs"],
        // Formate le Pourcentage en pourcentage avec deux décimales
        Pourcentage: item.Pourcentage.toFixed(2) + " %",
      }));

      // Crée une nouvelle feuille Excel avec les données
      const worksheet = XLSX.utils.json_to_sheet(data);

      // Ajoute des titres de colonnes (facultatif)
      const columns = [
        "ID",
        "Agence",
        "Tél",
        "Email",
        "Sexe/Genre",
        "Représentant",
        "Nombre de CC",
        "Total Erreurs",
        "Pourcentage",
      ];
      XLSX.utils.sheet_add_aoa(worksheet, [columns], { origin: "A1" });

      // Crée un classeur Excel
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, "Erreurs par Agence");

      // Génère et télécharge le fichier Excel
      const fileName = "erreurs_agence.xlsx";
      XLSX.writeFile(workbook, fileName);
    },

    calculateTotal(column, type) {
      // Vérification du type pour calculer uniquement pour le tableau choisi
      if (type === "cc") {
        return this.ccErrorCounts.reduce((sum, ccError) => {
          return sum + (ccError[column] || 0);
        }, 0);
      } else if (type === "agence") {
        return this.agenceErrorCounts.reduce((sum, agenceError) => {
          return sum + (agenceError[column] || 0);
        }, 0);
      }
      return 0; // Retourne 0 si le type est invalide
    },

    calculatePercentageTotal(column, type, totalErrors) {
      // Vérifie si le totalErrors est valide pour éviter une division par zéro
      if (!totalErrors || totalErrors <= 0) {
        return 0; // Retourne 0 si le total des erreurs est invalide
      }

      let totalColumnErrors = 0;

      // Calcul des erreurs en fonction du type
      if (type === "cc") {
        totalColumnErrors = this.ccErrorCounts.reduce((sum, ccError) => {
          return sum + (ccError[column] || 0);
        }, 0);
      } else if (type === "agence") {
        totalColumnErrors = this.agenceErrorCounts.reduce(
          (sum, agenceError) => {
            return sum + (agenceError[column] || 0);
          },
          0
        );
      }

      // Calcul du pourcentage par rapport au total des erreurs
      return ((totalColumnErrors / totalErrors) * 100).toFixed(2); // Pourcentage avec 2 décimales
    },
  },

  computed: {
    // Liste unique des CC pour le filtre
    uniqueAgences() {
      // Retourne une liste unique des agences disponibles
      return [...new Set(this.agenceErrorCounts.map((item) => item.Agence))];
    },
    filteredAgenceErrors() {
      // Retourne les erreurs filtrées par agence
      if (this.selectedAgence) {
        return this.agenceErrorCounts.filter(
          (item) => item.Agence === this.selectedAgence
        );
      }
      return this.agenceErrorCounts;
    },

    uniqueCCs() {
      return [...new Set(this.ccErrorCounts.map((cc) => cc.CC))];
    },

    // Regroupement des données par CC et Agence
    groupedErrors() {
      const grouped = {};

      // Regroupement des erreurs par CC et Agence
      this.ccErrorCounts.forEach((ccError) => {
        const key = `${ccError.CC}-${ccError.Agence}`;
        if (!grouped[key]) {
          grouped[key] = { ...ccError };
        } else {
          grouped[key]["Total Erreurs Agence"] +=
            ccError["Total Erreurs Agence"];
          grouped[key]["Format du Numéro de Téléphone Invalide"] +=
            ccError["Format du Numéro de Téléphone Invalide"];
          grouped[key]["Domaine ou Format de l'Email Invalide"] +=
            ccError["Domaine ou Format de l'Email Invalide"];
          grouped[key]["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] +=
            ccError["Sexe ou Genre Incorrect ou Manquant pour Entreprise"];
          grouped[key]["Représentant Légal Manquant"] +=
            ccError["Représentant Légal Manquant"];

          // Mise à jour du pourcentage, recalculé selon la somme totale des erreurs
          grouped[key]["Pourcentage Par Agence"] = (
            (grouped[key]["Total Erreurs Agence"] / this.totalErrors) *
            100
          ).toFixed(2);
        }
      });

      return Object.values(grouped);
    },

    // Données filtrées selon le CC sélectionné
    filteredErrors() {
      if (this.selectedCC) {
        return this.groupedErrors.filter((cc) => cc.CC === this.selectedCC);
      }
      return this.groupedErrors;
    },

    // Calcul des totaux pour les colonnes
    totalTel() {
      return this.filteredErrors.reduce(
        (sum, cc) => sum + (cc["Format du Numéro de Téléphone Invalide"] || 0),
        0
      );
    },
    totalEmail() {
      return this.filteredErrors.reduce(
        (sum, cc) => sum + (cc["Domaine ou Format de l'Email Invalide"] || 0),
        0
      );
    },
    totalSexeGenre() {
      return this.filteredErrors.reduce(
        (sum, cc) =>
          sum +
          (cc["Sexe ou Genre Incorrect ou Manquant pour Entreprise"] || 0),
        0
      );
    },
    totalRepresentant() {
      return this.filteredErrors.reduce(
        (sum, cc) => sum + (cc["Représentant Légal Manquant"] || 0),
        0
      );
    },
    totalErreursAgence() {
      return this.filteredErrors.reduce(
        (sum, cc) => sum + (cc["Total Erreurs Agence"] || 0),
        0
      );
    },
    totalPourcentageAgence() {
      const totalErreursAgence = this.filteredErrors.reduce(
        (sum, cc) => sum + (cc["Total Erreurs Agence"] || 0),
        0
      );

      // Limiter le pourcentage total à 100% si nécessaire
      return ((totalErreursAgence / this.totalErrors) * 100).toFixed(2);
    },
  },

  mounted() {
    document
      .getElementById("upload-button")
      .addEventListener("click", this.uploadFile);
    console.log("agenceErrorCounts:", this.agenceErrorCounts);

    this.$nextTick(() => {
      this.createChart(); // Create chart after data is set
    });
  },
};
</script>

<style scoped>
/* Ajout du style directement dans le HTML pour le texte value */
.custom-value-card .value {
  color: white !important;
}
</style>
