<script setup>
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { ref, onMounted } from 'vue';
import api from '../api';

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps(['userId']);
const chartData = ref({ labels: [], datasets: [] });
const loaded = ref(false);

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom' }
  }
};

onMounted(async () => {
  try {
    const { data } = await api.get(`/dashboard/expenses-chart/${props.userId}`);
    
    chartData.value = {
      labels: data.labels,
      datasets: [{
        ...data.datasets[0],
        backgroundColor: ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']
      }]
    };
    loaded.value = true;
  } catch (e) {
    console.error("Error cargando gráfica", e);
  }
});
</script>

<template>
  <div style="height: 300px;">
    <Doughnut v-if="loaded" :data="chartData" :options="chartOptions" />
    <p v-else>Cargando gráfica...</p>
  </div>
</template>