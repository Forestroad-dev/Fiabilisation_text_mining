<template>
  <div class="py-3 mb-3 border-radius-lg pe-1" :class="`bg-gradient-${color}`">
    <div class="chart">
      <canvas :id="id" class="chart-canvas" height="400"></canvas>
    </div>
  </div>
  <h6 class="mt-4 mb-0 ms-2">{{ title }}</h6>
  <!-- eslint-disable vue/no-v-html -->
  <p class="text-sm ms-2" v-html="description" />
  <div class="container border-radius-lg">
    <div class="row">
      <div
        v-for="(
          {
            label,
            progress: { content, percentage },
            icon: { color: colour, component },
          },
          index
        ) in items"
        :key="index"
        class="py-3 col-3 ps-0"
      >
        <div class="mb-2 d-flex">
          <div
            class="text-center shadow icon icon-shape icon-xxs border-radius-sm me-2 d-flex align-items-center justify-content-center"
            :class="`bg-gradient-${colour}`"
          >
            <font-awesome-icon
              :icon="component"
              size="xs"
              :style="{ color: 'white' }"
            />
          </div>
          <p class="mt-1 mb-0 text-xs font-weight-bold">{{ label }}</p>
        </div>
        <h4 class="font-weight-bolder">{{ content }}</h4>
        <div class="progress w-75">
          <div
            class="progress-bar bg-dark"
            :class="`w-${Math.min(Math.max(percentage, 0), 100)}`"
            role="progressbar"
            :aria-valuenow="percentage"
            aria-valuemin="0"
            aria-valuemax="100"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import Chart from "chart.js/auto";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

export default {
  name: "ReportsBarChart",
  components: {
    FontAwesomeIcon,
  },
  props: {
    id: {
      type: String,
      required: true,
    },
    color: {
      type: String,
      default: "dark",
    },
    title: {
      type: String,
      default: "",
    },
    description: {
      type: String,
      default: "",
    },
    chart: {
      type: Object,
      required: true,
      labels: Array,
      datasets: {
        type: Object,
        required: true,
      },
    },
    items: {
      type: Array,
      default: () => {
        [];
      },
    },
  },
  mounted() {
    const ctx = document.getElementById(this.id).getContext("2d");

    // Vérifiez les données
    if (!this.chart.labels || !this.chart.datasets.data) {
      console.error("Labels ou datasets non définis");
      return;
    }


    // Détruisez tout graphique existant
    const chartStatus = Chart.getChart(this.id);
    if (chartStatus) {
      chartStatus.destroy();
    }

    // Initialisez le graphique
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: [...this.chart.labels],
        datasets: [
          {
            label: this.chart.datasets.label,
            tension: 0.4,
            borderWidth: 0,
            borderRadius: 4,
            borderSkipped: false,
            backgroundColor: "#4CAF50",
            borderColor: "rgba(75, 192, 192, 1)",
            data: [...this.chart.datasets.data],
            maxBarThickness: 12, // Ajusté
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
        },
        interaction: {
          intersect: false,
          mode: "index",
        },
        scales: {
          y: {
            ticks: {
              color: "#fff", // Écriture blanche pour l'axe Y
              font: {
                size: 14, // Taille de la police
              },
            },
            grid: {
              color: "rgba(255, 255, 255, 0.1)", // Couleur blanche transparente pour la grille
            },
          },
          x: {
            ticks: {
              color: "#fff", // Écriture blanche pour l'axe X
              font: {
                size: 14,
              },
            },
            grid: {
              display: false, // Pas de grille pour l'axe X
            },
          },
        },

      },
    });
    // const canvas = document.getElementById(this.id);
    // canvas.style.height = "400px";
  }

};
</script>
