<script setup>
import * as echarts from 'echarts'
import { nextTick, onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Trophy, Document, TrendCharts, EditPen, Sunny, Calendar,
  Star, Flag, MagicStick,
} from '@element-plus/icons-vue'
import { knowledgeApi, pointsApi, userApi, growthApi } from '../api/modules'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const profile = ref(null)
const ranking = ref([])
const myKnowledge = ref([])
const loading = ref(true)
const chartRef = ref(null)
const growthStats = ref(null)
const checkinStatus = ref({ checked_in_today: false, streak_days: 0, month_count: 0 })
const aiCoach = ref(null)
const checkingIn = ref(false)

// 成长等级计算
const level = computed(() => Math.min(30, (profile.value?.total_points || 0) / 100 + 1 | 0))
const levelProgress = computed(() => {
  const pts = profile.value?.total_points || 0
  return Math.min(100, (pts % 100))
})
const levelTitle = computed(() => {
  const lv = level.value
  if (lv >= 25) return '知识圣者'
  if (lv >= 20) return '知识大师'
  if (lv >= 15) return '知识专家'
  if (lv >= 10) return '知识达人'
  if (lv >= 5) return '知识学徒'
  return '知识新手'
})

// 签到
const handleCheckin = async () => {
  checkingIn.value = true
  try {
    const res = await growthApi.checkin()
    checkinStatus.value = { checked_in_today: true, streak_days: res.streak_days, month_count: (checkinStatus.value.month_count || 0) + 1 }
    ElMessage.success(`签到成功！连续 ${res.streak_days} 天，+${res.points} 成长值`)
    // 刷新数据
    loadData()
  } catch {} finally { checkingIn.value = false }
}

// 统计卡片
const statsCards = computed(() => [
  { label: '累计成长值', value: profile.value?.total_points || 0, icon: TrendCharts, color: '#6366f1', bg: 'linear-gradient(135deg, #e0e7ff, #c7d2fe)' },
  { label: '知识总数', value: profile.value?.knowledge_count || 0, icon: Document, color: '#3b82f6', bg: 'linear-gradient(135deg, #dbeafe, #bfdbfe)' },
  { label: '连续签到', value: checkinStatus.value.streak_days, icon: Calendar, color: '#f59e0b', bg: 'linear-gradient(135deg, #fef3c7, #fde68a)' },
  { label: '勋章数', value: growthStats.value?.badge_count || 0, icon: Trophy, color: '#10b981', bg: 'linear-gradient(135deg, #d1fae5, #a7f3d0)' },
])

const renderChart = async () => {
  await nextTick()
  if (!chartRef.value || myKnowledge.value.length === 0) return
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e2e8f0',
      textStyle: { color: '#1e293b' },
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: myKnowledge.value.map((item) => item.title.length > 8 ? item.title.slice(0, 8) + '...' : item.title),
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#64748b', fontSize: 11, rotate: 15 },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#94a3b8' },
    },
    series: [{
      type: 'bar',
      data: myKnowledge.value.map((item) => item.contribution_score),
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#6366F1' },
          { offset: 1, color: '#818CF8' },
        ]),
      },
      barWidth: '45%',
    }],
  })
  window.addEventListener('resize', () => chart.resize())
}

const loadData = async () => {
  loading.value = true
  try {
    const isAdmin = authStore.isAdmin
    const [profileData, rankingData, knowledgeData, checkinData, statsData, coachData] = await Promise.all([
      userApi.profile(),
      pointsApi.ranking({ page: 1, page_size: 5 }),
      knowledgeApi.list(isAdmin ? { page: 1, page_size: 8 } : { mine: true, page: 1, page_size: 8 }),
      growthApi.checkinStatus().catch(() => ({ checked_in_today: false, streak_days: 0, month_count: 0 })),
      growthApi.stats().catch(() => null),
      growthApi.aiCoach().catch(() => null),
    ])
    profile.value = profileData
    ranking.value = rankingData.items || []
    myKnowledge.value = knowledgeData.items || []
    checkinStatus.value = checkinData
    growthStats.value = statsData
    aiCoach.value = coachData
    renderChart()
  } catch {} finally { loading.value = false }
}

onMounted(loadData)
</script>

<template>
  <div class="dashboard">
    <!-- 顶部横幅：成长等级 + 签到 -->
    <div class="welcome-banner">
      <div class="welcome-content">
        <div class="welcome-left">
          <div class="level-badge">
            <span class="level-num">Lv.{{ level }}</span>
          </div>
          <div class="welcome-text">
            <h1 class="welcome-title">{{ profile ? `${profile.real_name}，${levelTitle}` : 'KnowledgeOS' }}</h1>
            <p class="welcome-subtitle">AI 知识成长与能力运营平台 · 每一天都在进步</p>
            <div class="level-bar">
              <div class="level-bar-track">
                <div class="level-bar-fill" :style="{ width: levelProgress + '%' }"></div>
              </div>
              <span class="level-bar-text">{{ profile?.total_points || 0 }} / {{ level * 100 }} 成长值</span>
            </div>
          </div>
        </div>
        <div class="welcome-right">
          <div class="checkin-area">
            <div v-if="checkinStatus.checked_in_today" class="checkin-done">
              <el-icon :size="20" color="#10b981"><Sunny /></el-icon>
              <span>已签到 · 连续 <strong>{{ checkinStatus.streak_days }}</strong> 天</span>
            </div>
            <el-button
              v-else
              type="primary"
              size="large"
              :loading="checkingIn"
              @click="handleCheckin"
              class="checkin-btn"
            >
              <el-icon><Sunny /></el-icon> 每日签到
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stat-grid">
      <template v-if="loading">
        <div v-for="i in 4" :key="i" class="stat-card"><el-skeleton :rows="2" animated /></div>
      </template>
      <template v-else>
        <div v-for="(stat, idx) in statsCards" :key="idx" class="stat-card" :style="{ animationDelay: `${idx * 0.1}s` }">
          <div class="stat-icon" :style="{ background: stat.bg }">
            <el-icon :size="24" :style="{ color: stat.color }"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">{{ stat.label }}</div>
            <div class="stat-value">{{ stat.value }}</div>
          </div>
        </div>
      </template>
    </div>

    <!-- AI 成长教练 + 图表 -->
    <div class="dashboard-body">
      <div class="page-card chart-section">
        <div class="page-header">
          <h3 class="section-title">
            <el-icon style="margin-right: 6px; color: #6366f1;"><MagicStick /></el-icon>
            {{ authStore.isAdmin ? '平台知识贡献趋势' : '我的知识贡献趋势' }}
          </h3>
        </div>
        <el-skeleton v-if="loading" :rows="6" animated />
        <template v-else>
          <div v-if="myKnowledge.length" ref="chartRef" class="chart-box" />
          <el-empty v-else description="暂无知识数据，快去发布吧">
            <el-button type="primary" @click="router.push('/app/publish')">发布第一篇知识</el-button>
          </el-empty>
        </template>
      </div>

      <!-- AI 教练建议 -->
      <div class="page-card coach-section">
        <div class="page-header">
          <h3 class="section-title">
            <el-icon style="margin-right: 6px; color: #f59e0b;"><MagicStick /></el-icon>
            AI 成长教练
          </h3>
        </div>
        <el-skeleton v-if="loading" :rows="4" animated />
        <template v-else>
          <div v-if="aiCoach" class="coach-content">
            <!-- 今日目标 -->
            <div class="coach-goal">
              <div class="goal-title">今日学习目标</div>
              <div class="goal-items">
                <div class="goal-item">
                  <el-icon :size="16" color="#6366f1"><Document /></el-icon>
                  <span>阅读 {{ aiCoach.today_goal.target_reads }} 篇知识</span>
                  <el-progress :percentage="Math.min(100, (aiCoach.today_goal.actual_reads / aiCoach.today_goal.target_reads) * 100)" :stroke-width="6" :show-text="false" style="flex: 1; margin: 0 12px;" />
                  <span class="goal-count">{{ aiCoach.today_goal.actual_reads }}/{{ aiCoach.today_goal.target_reads }}</span>
                </div>
                <div class="goal-item">
                  <el-icon :size="16" color="#10b981"><EditPen /></el-icon>
                  <span>发布 {{ aiCoach.today_goal.target_publish }} 篇知识</span>
                  <el-progress :percentage="Math.min(100, (aiCoach.today_goal.actual_publish / aiCoach.today_goal.target_publish) * 100)" :stroke-width="6" :show-text="false" style="flex: 1; margin: 0 12px;" />
                  <span class="goal-count">{{ aiCoach.today_goal.actual_publish }}/{{ aiCoach.today_goal.target_publish }}</span>
                </div>
              </div>
            </div>
            <!-- AI 建议 -->
            <div class="coach-suggestions">
              <div class="suggestion-title">成长建议</div>
              <div v-for="(s, i) in aiCoach.suggestions" :key="i" class="suggestion-item" :class="'suggestion-' + s.priority">
                <el-icon :size="14"><Flag /></el-icon>
                <span>{{ s.text }}</span>
              </div>
              <div v-if="!aiCoach.suggestions.length" class="suggestion-item suggestion-low">
                <el-icon :size="14"><Star /></el-icon>
                <span>你做得很好！继续保持学习节奏</span>
              </div>
            </div>
          </div>
          <el-empty v-else description="AI 教练加载中..." :image-size="60" />
        </template>
      </div>
    </div>

    <!-- 排行榜 + 最近知识 -->
    <div class="dashboard-body">
      <!-- 排行榜 -->
      <div class="page-card ranking-section">
        <div class="page-header">
          <h3 class="section-title">成长值排行榜 TOP5</h3>
          <el-button text type="primary" @click="router.push('/app/ranking')">查看全部</el-button>
        </div>
        <el-skeleton v-if="loading" :rows="5" animated />
        <div v-else class="ranking-list">
          <div v-for="(item, idx) in ranking" :key="item.user_id" class="ranking-item" :style="{ animationDelay: `${idx * 0.08}s` }">
            <div class="rank-badge" :class="{ 'top-1': idx === 0, 'top-2': idx === 1, 'top-3': idx === 2 }">{{ idx + 1 }}</div>
            <el-avatar :size="36" class="rank-avatar">{{ item.real_name?.charAt(0) || 'U' }}</el-avatar>
            <div class="rank-info">
              <div class="rank-name">{{ item.real_name }}</div>
              <div class="rank-dept">{{ item.department || '未设置部门' }}</div>
            </div>
            <div class="rank-points">{{ item.total_points }}</div>
          </div>
          <el-empty v-if="!ranking.length" description="暂无排行数据" :image-size="80" />
        </div>
      </div>

      <!-- 最近知识 -->
      <div class="page-card">
        <div class="page-header">
          <h3 class="section-title">最近发布的知识</h3>
          <el-button text type="primary" @click="router.push('/app/knowledge')">查看全部</el-button>
        </div>
        <el-skeleton v-if="loading" :rows="4" animated />
        <div v-else class="recent-list">
          <div v-for="item in myKnowledge.slice(0, 5)" :key="item.id" class="recent-item">
            <el-tag :type="item.status === 'approved' ? 'success' : item.status === 'pending' ? 'warning' : 'danger'" size="small" effect="plain">
              {{ item.status === 'approved' ? '已通过' : item.status === 'pending' ? '审核中' : '已驳回' }}
            </el-tag>
            <span class="recent-title">{{ item.title }}</span>
            <span class="recent-meta">{{ item.category }} · {{ item.view_count }} 浏览</span>
          </div>
          <el-empty v-if="!myKnowledge.length" description="暂无知识" :image-size="60">
            <el-button type="primary" size="small" @click="router.push('/app/publish')">去发布</el-button>
          </el-empty>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 20px; }

/* ---- Welcome Banner ---- */
.welcome-banner {
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
  border-radius: 20px;
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
}
.welcome-banner::before {
  content: '';
  position: absolute;
  top: -60%;
  right: -10%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(99,102,241,0.25), transparent 70%);
  pointer-events: none;
}
.welcome-banner::after {
  content: '';
  position: absolute;
  bottom: -40%;
  left: 20%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(245,158,11,0.1), transparent 70%);
  pointer-events: none;
}
.welcome-content { position: relative; z-index: 1; display: flex; align-items: center; justify-content: space-between; }
.welcome-left { display: flex; align-items: center; gap: 20px; }
.level-badge {
  width: 64px; height: 64px;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  border-radius: 18px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 24px rgba(99,102,241,0.4);
}
.level-num { color: #fff; font-size: 22px; font-weight: 800; }
.welcome-title { color: #fff; font-size: 22px; font-weight: 700; margin-bottom: 6px; }
.welcome-subtitle { color: rgba(255,255,255,0.45); font-size: 13px; margin-bottom: 12px; }
.level-bar { display: flex; align-items: center; gap: 12px; }
.level-bar-track { width: 200px; height: 8px; background: rgba(255,255,255,0.1); border-radius: 999px; overflow: hidden; }
.level-bar-fill { height: 100%; background: linear-gradient(90deg, #6366F1, #A78BFA); border-radius: 999px; transition: width 0.6s ease; }
.level-bar-text { font-size: 12px; color: rgba(255,255,255,0.5); }

/* ---- Check-in ---- */
.checkin-area { display: flex; align-items: center; }
.checkin-done {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 20px;
  background: rgba(16,185,129,0.12);
  border: 1px solid rgba(16,185,129,0.25);
  border-radius: 12px;
  color: #6ee7b7;
  font-size: 14px;
}
.checkin-done strong { color: #34d399; font-size: 16px; }
.checkin-btn {
  border-radius: 12px !important;
  padding: 12px 28px !important;
  font-weight: 600 !important;
  background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
  border: none !important;
  box-shadow: 0 4px 16px rgba(99,102,241,0.3);
}

/* ---- Stats ---- */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.stat-card {
  background: var(--color-bg-card, #fff);
  border-radius: 16px;
  padding: 20px;
  display: flex; align-items: center; gap: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  border: 1px solid rgba(0,0,0,0.04);
  animation: fadeInUp 0.4s ease both;
  transition: all 0.25s ease;
}
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
.stat-icon { width: 52px; height: 52px; border-radius: 14px; display: flex; align-items: center; justify-content: center; }
.stat-label { font-size: 13px; color: #64748b; margin-bottom: 4px; }
.stat-value { font-size: 26px; font-weight: 800; color: #0f172a; letter-spacing: -0.5px; }

/* ---- Body Grid ---- */
.dashboard-body { display: grid; grid-template-columns: 1.5fr 1fr; gap: 20px; }
.section-title { font-size: 15px; font-weight: 600; color: #1e293b; margin: 0; display: flex; align-items: center; }
.chart-box { height: 280px; }

/* ---- AI Coach ---- */
.coach-content { display: flex; flex-direction: column; gap: 20px; }
.coach-goal { background: #f8fafc; border-radius: 14px; padding: 16px; }
.goal-title { font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 12px; }
.goal-items { display: flex; flex-direction: column; gap: 10px; }
.goal-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #475569; }
.goal-count { font-size: 12px; color: #94a3b8; white-space: nowrap; }
.coach-suggestions { display: flex; flex-direction: column; gap: 8px; }
.suggestion-title { font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 4px; }
.suggestion-item {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 13px;
  color: #475569;
}
.suggestion-high { background: rgba(239,68,68,0.06); color: #dc2626; }
.suggestion-medium { background: rgba(245,158,11,0.06); color: #d97706; }
.suggestion-low { background: rgba(16,185,129,0.06); color: #059669; }

/* ---- Ranking ---- */
.ranking-list { display: flex; flex-direction: column; gap: 4px; }
.ranking-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px; border-radius: 12px;
  transition: background 0.2s ease;
  animation: fadeInUp 0.4s ease both;
}
.ranking-item:hover { background: #f8fafc; }
.rank-badge {
  width: 26px; height: 26px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 12px; background: #f1f5f9; color: #64748b;
}
.rank-badge.top-1 { background: linear-gradient(135deg, #f59e0b, #fbbf24); color: #fff; }
.rank-badge.top-2 { background: linear-gradient(135deg, #94a3b8, #cbd5e1); color: #fff; }
.rank-badge.top-3 { background: linear-gradient(135deg, #d97706, #f59e0b); color: #fff; }
.rank-avatar { background: linear-gradient(135deg, #6366F1, #8B5CF6); color: #fff; font-weight: 600; font-size: 14px; }
.rank-info { flex: 1; }
.rank-name { font-size: 13px; font-weight: 600; color: #1e293b; }
.rank-dept { font-size: 11px; color: #94a3b8; margin-top: 1px; }
.rank-points { font-size: 14px; font-weight: 700; color: #6366f1; }

/* ---- Recent ---- */
.recent-list { display: flex; flex-direction: column; gap: 4px; }
.recent-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 10px;
  transition: background 0.2s ease;
}
.recent-item:hover { background: #f8fafc; }
.recent-title { flex: 1; font-size: 13px; font-weight: 500; color: #1e293b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.recent-meta { font-size: 12px; color: #94a3b8; white-space: nowrap; }

@keyframes fadeInUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 1200px) {
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
  .dashboard-body { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .stat-grid { grid-template-columns: 1fr; }
  .welcome-content { flex-direction: column; gap: 16px; }
  .welcome-left { flex-direction: column; }
}
</style>
