<template>
  <div class="dashboard-pannel">
    <header>
      <h1>Resumen de Gastos Mensuales</h1>
    </header>
    
    <div class="grid">
      <div class="card">
        <h3>Distribución por Categoría</h3>
        <ExpenseChart :userId="1" /> 
      </div>

      <div class="card summary">
        <h3>Total Gastado</h3>
        <p class="amount text-red">$ {{ totalExpenses }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import ExpenseChart from '../components/ExpenseChart.vue';
// Aquí añadirías lógica para el total gastado...
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; padding: 20px; }
.card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.amount { font-size: 2rem; font-weight: bold; }
.text-red { color: #ef4444; }
</style>