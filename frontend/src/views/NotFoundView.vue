<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="not-found">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h2 class="error-title">页面未找到</h2>
      <p class="error-desc">抱歉，您访问的页面不存在或已被移除。</p>
      <div class="error-actions">
        <el-button type="primary" size="large" @click="router.push('/app/dashboard')">返回首页</el-button>
        <el-button size="large" @click="router.back()">返回上页</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-page);
}
.not-found-content { text-align: center; }
.error-code {
  font-size: 120px;
  font-weight: 900;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  margin-bottom: 16px;
}
.error-title { font-size: 24px; font-weight: 700; color: var(--color-text-primary); margin-bottom: 8px; }
.error-desc { font-size: 14px; color: var(--color-text-secondary); margin-bottom: 32px; }
.error-actions { display: flex; gap: 12px; justify-content: center; }
</style>
