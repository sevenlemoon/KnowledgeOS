<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const isAuthPage = computed(() => ['/login', '/register'].includes(route.path))
</script>

<template>
  <!-- Aurora 背景（仅非登录页显示） -->
  <div v-if="!isAuthPage" class="aurora-bg">
    <div class="aurora-orb aurora-orb-1"></div>
    <div class="aurora-orb aurora-orb-2"></div>
    <div class="aurora-orb aurora-orb-3"></div>
    <div class="aurora-orb aurora-orb-4"></div>
  </div>
  <router-view />
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}
</style>
