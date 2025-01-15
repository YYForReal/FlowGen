<template>
  <div class="app">
    <h1>科研绘图助手</h1>
    <PlantUMLRenderer />
  </div>
</template>

<script setup>
import PlantUMLRenderer from './components/PlantUMLRenderer.vue'
</script>

<style scoped>
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  color: #333;
}
</style>
