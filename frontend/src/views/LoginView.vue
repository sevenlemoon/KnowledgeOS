<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { authApi } from '../api/modules'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const rememberMe = ref(false)
const formRef = ref(null)
const form = reactive({
  username: '',
  password: '',
})
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    const response = await authApi.login(form)
    authStore.setSession(response.access_token, response.user)
    if (rememberMe.value) {
      localStorage.setItem('remembered_user', form.username)
    } else {
      localStorage.removeItem('remembered_user')
    }
    ElMessage.success('登录成功')
    router.push('/app/dashboard')
  } catch {
    // 错误已由 http 拦截器处理
  } finally {
    loading.value = false
  }
}

// 记住密码恢复
const remembered = localStorage.getItem('remembered_user')
if (remembered) {
  form.username = remembered
  rememberMe.value = true
}
</script>

<template>
  <div class="login-wrapper">
    <!-- 背景装饰 -->
    <div class="login-bg">
      <div class="bg-orb bg-orb-1"></div>
      <div class="bg-orb bg-orb-2"></div>
      <div class="bg-orb bg-orb-3"></div>
      <div class="bg-grid"></div>
    </div>

    <div class="login-container">
      <!-- 左侧品牌区 -->
      <div class="login-brand">
        <div class="brand-content">
          <div class="brand-logo">
            <div class="logo-mark">K</div>
            <span class="logo-name">KnowledgeOS</span>
          </div>
          <h1 class="brand-title">
            软件项目团队<br /><span class="gradient-text">知识共享与创新激励系统</span>
          </h1>
          <p class="brand-desc">
            构建高效的知识管理体系，激发团队创新活力。<br />
            让每一份知识都能创造价值，让每一次分享都获得认可。
          </p>
          <div class="brand-features">
            <div class="feature-item">
              <div class="feature-icon">📚</div>
              <div class="feature-text">
                <div class="feature-label">知识管理</div>
                <div class="feature-detail">结构化知识沉淀</div>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🏆</div>
              <div class="feature-text">
                <div class="feature-label">积分激励</div>
                <div class="feature-detail">量化贡献价值</div>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">👥</div>
              <div class="feature-text">
                <div class="feature-label">团队协作</div>
                <div class="feature-detail">促进知识流通</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录区 -->
      <div class="login-form-wrapper">
        <div class="login-card">
          <div class="card-header">
            <h2 class="card-title">欢迎回来</h2>
            <p class="card-subtitle">登录您的账号以继续</p>
          </div>

          <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin" class="login-form">
            <el-form-item prop="username">
              <el-input
                v-model="form.username"
                placeholder="请输入用户名"
                size="large"
                :prefix-icon="User"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                :prefix-icon="Lock"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住密码</el-checkbox>
              <a href="javascript:void(0)" class="forgot-link">忘记密码？</a>
            </div>

            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="login-btn"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登 录' }}
            </el-button>
          </el-form>

          <div class="card-footer">
            <span class="footer-text">还没有账号？</span>
            <router-link to="/register" class="footer-link">立即注册</router-link>
          </div>

          <div class="card-demo">
            <el-divider>演示账号</el-divider>
            <div class="demo-accounts">
              <el-tag effect="plain" class="demo-tag">管理员: admin / admin123456</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
  position: relative;
  overflow: hidden;
}

/* ---- Background ---- */
.login-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
}

.bg-orb-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  top: -200px;
  right: -100px;
}

.bg-orb-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  bottom: -150px;
  left: -100px;
}

.bg-orb-3 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #06b6d4, #3b82f6);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.2;
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 60px 60px;
}

/* ---- Container ---- */
.login-container {
  display: flex;
  width: 960px;
  min-height: 600px;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.12);
  position: relative;
  z-index: 1;
}

/* ---- Brand ---- */
.login-brand {
  flex: 1;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  padding: 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.login-brand::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
}

.brand-content {
  position: relative;
  z-index: 1;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 40px;
}

.logo-mark {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 20px;
  color: #fff;
}

.logo-name {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
}

.brand-title {
  color: #fff;
  font-size: 28px;
  font-weight: 700;
  line-height: 1.4;
  margin-bottom: 16px;
  letter-spacing: -0.5px;
}

.brand-title .gradient-text {
  background: linear-gradient(135deg, #60a5fa, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-desc {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  line-height: 1.8;
  margin-bottom: 40px;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.25s ease;
}
.feature-item:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateX(4px);
}

.feature-icon {
  font-size: 24px;
}

.feature-label {
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.feature-detail {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  margin-top: 2px;
}

/* ---- Form ---- */
.login-form-wrapper {
  width: 420px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
}

.login-card {
  width: 100%;
}

.card-header {
  margin-bottom: 32px;
}

.card-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.card-subtitle {
  font-size: 14px;
  color: #94a3b8;
}

.login-form {
  margin-bottom: 0;
}

.login-form :deep(.el-input__wrapper) {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 4px 12px;
  box-shadow: none;
  transition: all 0.25s ease;
}
.login-form :deep(.el-input__wrapper:hover) {
  border-color: #cbd5e1;
}
.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.forgot-link {
  font-size: 13px;
  color: #3b82f6;
  text-decoration: none;
}
.forgot-link:hover {
  color: #2563eb;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border: none;
  letter-spacing: 2px;
  transition: all 0.3s ease;
}
.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.35);
}

.card-footer {
  text-align: center;
  margin-top: 24px;
}

.footer-text {
  color: #94a3b8;
  font-size: 14px;
}

.footer-link {
  color: #3b82f6;
  font-weight: 500;
  margin-left: 4px;
}

.card-demo {
  margin-top: 24px;
}

.card-demo :deep(.el-divider__text) {
  font-size: 12px;
  color: #cbd5e1;
}

.demo-accounts {
  text-align: center;
}

.demo-tag {
  font-size: 12px;
}

/* ---- Responsive ---- */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    width: 92%;
    min-height: auto;
    margin: 20px;
  }
  .login-brand {
    padding: 32px;
    min-height: 200px;
  }
  .brand-title {
    font-size: 22px;
  }
  .brand-features {
    display: none;
  }
  .login-form-wrapper {
    width: 100%;
    padding: 32px;
  }
}
</style>
