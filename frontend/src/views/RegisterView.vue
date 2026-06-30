<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, OfficeBuilding } from '@element-plus/icons-vue'
import { authApi } from '../api/modules'

const router = useRouter()
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
  real_name: '',
  department: '',
  email: '',
})

const passwordStrength = computed(() => {
  const p = form.password
  if (!p) return { level: 0, text: '', color: '' }
  let score = 0
  if (p.length >= 6) score++
  if (p.length >= 10) score++
  if (/[A-Z]/.test(p)) score++
  if (/[0-9]/.test(p)) score++
  if (/[^A-Za-z0-9]/.test(p)) score++
  if (score <= 1) return { level: 1, text: '弱', color: '#ef4444' }
  if (score <= 3) return { level: 2, text: '中', color: '#f59e0b' }
  return { level: 3, text: '强', color: '#10b981' }
})

const handleRegister = async () => {
  if (!form.username || !form.password || !form.real_name) {
    ElMessage.warning('请填写必填项')
    return
  }
  loading.value = true
  try {
    await authApi.register(form)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch {
    // 错误已由 http 拦截器处理
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrapper">
    <div class="login-bg">
      <div class="bg-orb bg-orb-1"></div>
      <div class="bg-orb bg-orb-2"></div>
      <div class="bg-grid"></div>
    </div>

    <div class="login-container">
      <!-- 左侧品牌区 -->
      <div class="login-brand">
        <div class="brand-content">
          <div class="brand-logo">
            <div class="logo-mark">K</div>
            <span class="logo-name">知识共享平台</span>
          </div>
          <h1 class="brand-title">
            加入<span class="gradient-text">知识共享</span><br />创新激励平台
          </h1>
          <p class="brand-desc">
            注册成为团队成员，开始分享知识、积累积分、提升影响力。
          </p>
          <div class="brand-steps">
            <div class="step-item">
              <div class="step-num">1</div>
              <div class="step-text">注册账号</div>
            </div>
            <div class="step-line"></div>
            <div class="step-item">
              <div class="step-num">2</div>
              <div class="step-text">发布知识</div>
            </div>
            <div class="step-line"></div>
            <div class="step-item">
              <div class="step-num">3</div>
              <div class="step-text">获得积分</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧注册区 -->
      <div class="login-form-wrapper">
        <div class="login-card">
          <div class="card-header">
            <h2 class="card-title">创建账号</h2>
            <p class="card-subtitle">注册后即可参与团队知识共享与积分激励</p>
          </div>

          <el-form :model="form" @submit.prevent="handleRegister" class="login-form">
            <el-form-item>
              <el-input
                v-model="form.username"
                placeholder="用户名 (4-20位)"
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="form.real_name"
                placeholder="真实姓名"
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="form.department"
                placeholder="部门 (选填)"
                size="large"
                :prefix-icon="OfficeBuilding"
              />
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="form.email"
                placeholder="邮箱 (选填)"
                size="large"
                :prefix-icon="Message"
              />
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="form.password"
                type="password"
                placeholder="密码 (6-20位)"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
              <!-- 密码强度指示器 -->
              <div v-if="form.password" class="password-strength">
                <div class="strength-bars">
                  <div
                    v-for="i in 3"
                    :key="i"
                    class="strength-bar"
                    :style="{ background: i <= passwordStrength.level ? passwordStrength.color : '#e2e8f0' }"
                  ></div>
                </div>
                <span class="strength-text" :style="{ color: passwordStrength.color }">
                  {{ passwordStrength.text }}
                </span>
              </div>
            </el-form-item>

            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="login-btn"
              @click="handleRegister"
            >
              {{ loading ? '注册中...' : '注 册' }}
            </el-button>
          </el-form>

          <div class="card-footer">
            <span class="footer-text">已有账号？</span>
            <router-link to="/login" class="footer-link">返回登录</router-link>
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
.login-bg { position: absolute; inset: 0; z-index: 0; }
.bg-orb { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.4; }
.bg-orb-1 { width: 500px; height: 500px; background: linear-gradient(135deg, #667eea, #764ba2); top: -200px; right: -100px; }
.bg-orb-2 { width: 400px; height: 400px; background: linear-gradient(135deg, #3b82f6, #2563eb); bottom: -150px; left: -100px; }
.bg-grid { position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px); background-size: 60px 60px; }

.login-container { display: flex; width: 960px; min-height: 640px; border-radius: 24px; overflow: hidden; box-shadow: 0 25px 60px rgba(0,0,0,0.12); position: relative; z-index: 1; }
.login-brand { flex: 1; background: linear-gradient(135deg, #0f172a, #1e293b); padding: 48px; display: flex; flex-direction: column; justify-content: center; position: relative; overflow: hidden; }
.login-brand::before { content: ''; position: absolute; top: -50%; right: -50%; width: 100%; height: 100%; background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%); }
.brand-content { position: relative; z-index: 1; }
.brand-logo { display: flex; align-items: center; gap: 12px; margin-bottom: 40px; }
.logo-mark { width: 40px; height: 40px; background: linear-gradient(135deg, #3b82f6, #6366f1); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 20px; color: #fff; }
.logo-name { color: #fff; font-size: 18px; font-weight: 600; }
.brand-title { color: #fff; font-size: 28px; font-weight: 700; line-height: 1.4; margin-bottom: 16px; }
.brand-title .gradient-text { background: linear-gradient(135deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.brand-desc { color: rgba(255,255,255,0.6); font-size: 14px; line-height: 1.8; margin-bottom: 40px; }

.brand-steps { display: flex; align-items: center; gap: 12px; }
.step-item { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.step-num { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #3b82f6, #6366f1); display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 700; font-size: 14px; }
.step-text { color: rgba(255,255,255,0.6); font-size: 12px; }
.step-line { flex: 1; height: 1px; background: rgba(255,255,255,0.15); margin-top: -20px; }

.login-form-wrapper { width: 420px; background: rgba(255,255,255,0.95); backdrop-filter: blur(20px); display: flex; align-items: center; justify-content: center; padding: 40px; }
.login-card { width: 100%; }
.card-header { margin-bottom: 24px; }
.card-title { font-size: 24px; font-weight: 700; color: #1e293b; margin-bottom: 8px; }
.card-subtitle { font-size: 14px; color: #94a3b8; }

.login-form :deep(.el-input__wrapper) { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 4px 12px; box-shadow: none; transition: all 0.25s ease; }
.login-form :deep(.el-input__wrapper:hover) { border-color: #cbd5e1; }
.login-form :deep(.el-input__wrapper.is-focus) { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }

.password-strength { display: flex; align-items: center; gap: 8px; margin-top: 6px; width: 100%; }
.strength-bars { display: flex; gap: 4px; flex: 1; }
.strength-bar { height: 4px; flex: 1; border-radius: 2px; transition: background 0.3s ease; }
.strength-text { font-size: 12px; font-weight: 500; }

.login-btn { width: 100%; height: 48px; font-size: 16px; font-weight: 600; border-radius: 12px; background: linear-gradient(135deg, #2563eb, #3b82f6); border: none; letter-spacing: 2px; transition: all 0.3s ease; }
.login-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(37,99,235,0.35); }

.card-footer { text-align: center; margin-top: 20px; }
.footer-text { color: #94a3b8; font-size: 14px; }
.footer-link { color: #3b82f6; font-weight: 500; margin-left: 4px; }

@media (max-width: 768px) {
  .login-container { flex-direction: column; width: 92%; min-height: auto; margin: 20px; }
  .login-brand { padding: 32px; min-height: 180px; }
  .brand-steps { display: none; }
  .login-form-wrapper { width: 100%; padding: 24px; }
}
</style>
