<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Odometer, Collection, EditPen, Trophy, User, Setting,
  Fold, Expand, Bell, SwitchButton, Search,
} from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const collapsed = ref(false)
const searchKeyword = ref('')

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push({ path: '/app/knowledge', query: { keyword: searchKeyword.value.trim() } })
    searchKeyword.value = ''
  }
}

const menus = computed(() => {
  const base = [
    { label: '成长工作台', path: '/app/dashboard', icon: Odometer },
    { label: '知识库', path: '/app/knowledge', icon: Collection },
    { label: '发布知识', path: '/app/publish', icon: EditPen },
    { label: '排行榜', path: '/app/ranking', icon: Trophy },
    { label: '我的', path: '/app/profile', icon: User },
  ]
  if (authStore.isAdmin) {
    base.push({ label: '后台审核', path: '/app/admin', icon: Setting })
  }
  return base
})

const activeMenu = computed(() => route.path)
const sidebarWidth = computed(() => collapsed.value ? '68px' : '240px')

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="sidebarWidth" class="layout-sidebar">
      <div class="sidebar-logo" :class="{ collapsed }">
        <div class="logo-icon">K</div>
        <transition name="fade">
          <div v-if="!collapsed" class="logo-text-group">
            <span class="logo-text">KnowledgeOS</span>
            <span class="logo-slogan">AI 知识成长平台</span>
          </div>
        </transition>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        class="sidebar-menu"
        router
        :collapse-transition="false"
      >
        <el-menu-item
          v-for="menu in menus"
          :key="menu.path"
          :index="menu.path"
          class="sidebar-menu-item"
        >
          <el-icon><component :is="menu.icon" /></el-icon>
          <template #title>{{ menu.label }}</template>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <div class="collapse-btn" @click="collapsed = !collapsed">
          <el-icon><Fold v-if="!collapsed" /><Expand v-else /></el-icon>
        </div>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="layout-main">
      <!-- 顶部导航 -->
      <el-header class="layout-header">
        <div class="header-left">
          <div class="header-search" @click="$refs.searchInput?.focus()">
            <el-icon class="search-icon"><Search /></el-icon>
            <input
              ref="searchInput"
              v-model="searchKeyword"
              class="search-input"
              placeholder="搜索知识..."
              @keyup.enter="handleSearch"
            />
            <kbd class="search-kbd">Enter</kbd>
          </div>
        </div>
        <div class="header-right">
          <el-badge :value="0" :hidden="true" class="header-badge">
            <el-button :icon="Bell" circle size="small" text />
          </el-badge>
          <el-divider direction="vertical" style="height: 20px; margin: 0 4px;" />
          <el-dropdown trigger="click">
            <div class="header-user">
              <el-avatar :size="34" class="user-avatar">
                {{ authStore.user?.real_name?.charAt(0) || 'U' }}
              </el-avatar>
              <div class="user-info">
                <span class="user-name">{{ authStore.user?.real_name }}</span>
                <span class="user-role">{{ authStore.isAdmin ? '管理员' : '成员' }}</span>
              </div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/app/profile')">
                  <el-icon><User /></el-icon> 个人中心
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 页面内容 -->
      <el-main class="layout-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-container { min-height: 100vh; }

/* ---- Sidebar ---- */
.layout-sidebar {
  background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  transition: width var(--transition-slow);
  overflow: hidden;
  position: fixed;
  left: 0; top: 0; bottom: 0;
  z-index: 100;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 16px;
  height: 72px;
  transition: all var(--transition-normal);
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
.sidebar-logo.collapsed { justify-content: center; padding: 20px 0; }

.logo-icon {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 18px; color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.logo-text-group { display: flex; flex-direction: column; }
.logo-text { font-size: 15px; font-weight: 700; white-space: nowrap; letter-spacing: 0.3px; }
.logo-slogan { font-size: 11px; color: rgba(255, 255, 255, 0.35); white-space: nowrap; margin-top: 1px; }

.sidebar-menu {
  flex: 1;
  border: none !important;
  background: transparent !important;
  padding: 12px 10px;
}
.sidebar-menu:not(.el-menu--collapse) { width: 100%; }

.sidebar-menu-item {
  border-radius: 14px !important;
  margin-bottom: 4px;
  height: 44px;
  color: rgba(255, 255, 255, 0.55) !important;
  transition: all var(--transition-normal);
  font-weight: 500;
}
.sidebar-menu-item:hover {
  background: rgba(255, 255, 255, 0.06) !important;
  color: rgba(255, 255, 255, 0.9) !important;
}
.sidebar-menu-item.is-active {
  background: linear-gradient(135deg, #4F46E5, #7C3AED) !important;
  color: #fff !important;
  box-shadow: 0 4px 16px rgba(79, 70, 229, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}
.collapse-btn {
  display: flex; align-items: center; justify-content: center;
  height: 36px; border-radius: 10px; cursor: pointer;
  color: rgba(255, 255, 255, 0.4);
  transition: all var(--transition-normal);
}
.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.8);
}

/* ---- Main ---- */
.layout-main {
  margin-left: v-bind(sidebarWidth);
  transition: margin-left var(--transition-slow);
}

/* ---- Header ---- */
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-xl);
  height: var(--header-height);
  position: sticky; top: 0; z-index: 90;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.header-search {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 16px;
  background: rgba(241, 245, 249, 0.8);
  border-radius: 12px;
  cursor: pointer;
  transition: all var(--transition-normal);
  min-width: 280px;
}
.header-search:hover { background: rgba(241, 245, 249, 1); }
.search-icon { color: var(--color-text-placeholder); font-size: 16px; }
.search-placeholder { color: var(--color-text-placeholder); font-size: 13px; }
.search-input {
  border: none; outline: none; background: transparent;
  font-size: 13px; color: var(--color-text-primary);
  flex: 1; min-width: 0; font-family: inherit;
}
.search-input::placeholder { color: var(--color-text-placeholder); }
.search-kbd {
  margin-left: auto;
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 11px;
  color: var(--color-text-placeholder);
  font-family: inherit;
}

.header-right { display: flex; align-items: center; gap: 8px; }
.header-badge { display: flex; align-items: center; }

.header-user {
  display: flex; align-items: center; gap: 10px;
  cursor: pointer; padding: 6px 10px;
  border-radius: 12px; transition: background var(--transition-fast);
}
.header-user:hover { background: rgba(241, 245, 249, 0.8); }

.user-avatar {
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: #fff; font-weight: 600; font-size: 14px;
}

.user-info { display: flex; flex-direction: column; }
.user-name { font-size: 13px; font-weight: 600; color: var(--color-text-primary); line-height: 1.2; }
.user-role { font-size: 11px; color: var(--color-text-secondary); line-height: 1.2; }

/* ---- Content ---- */
.layout-content {
  padding: var(--space-xl);
  min-height: calc(100vh - var(--header-height));
  background: transparent;
  position: relative;
  z-index: 1;
}
</style>
