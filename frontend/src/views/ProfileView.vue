<script setup>
import * as echarts from 'echarts'
import { nextTick, onMounted, ref, computed } from 'vue'
import {
  Trophy, Document, TrendCharts, Medal, Star, View,
  CollectionTag, Calendar, MagicStick, Flag, Clock, ChatDotRound,
} from '@element-plus/icons-vue'
import { pointsApi, userApi, growthApi, knowledgeApi } from '../api/modules'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const profile = ref(null)
const records = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const chartRef = ref(null)
const badges = ref([])
const myKnowledge = ref([])
const growthStats = ref(null)
const loading = ref(true)

// 成长等级
const level = computed(() => Math.min(30, (profile.value?.total_points || 0) / 100 + 1 | 0))
const levelTitle = computed(() => {
  const lv = level.value
  if (lv >= 25) return '知识圣者'
  if (lv >= 20) return '知识大师'
  if (lv >= 15) return '知识专家'
  if (lv >= 10) return '知识达人'
  if (lv >= 5) return '知识学徒'
  return '知识新手'
})

// GitHub 风格热力图数据
const heatmapData = computed(() => {
  const map = {}
  records.value.forEach(r => {
    const date = r.create_time?.slice(0, 10)
    if (date) {
      map[date] = (map[date] || 0) + 1
    }
  })
  return map
})

// 生成最近 52 周的日期网格
const heatmapWeeks = computed(() => {
  const weeks = []
  const today = new Date()
  const startDate = new Date(today)
  startDate.setDate(startDate.getDate() - 364)
  // 调整到周日
  startDate.setDate(startDate.getDate() - startDate.getDay())

  let currentWeek = []
  const d = new Date(startDate)
  while (d <= today) {
    const dateStr = d.toISOString().slice(0, 10)
    const count = heatmapData.value[dateStr] || 0
    currentWeek.push({ date: dateStr, count, day: d.getDay() })
    if (d.getDay() === 6) {
      weeks.push(currentWeek)
      currentWeek = []
    }
    d.setDate(d.getDate() + 1)
  }
  if (currentWeek.length) weeks.push(currentWeek)
  return weeks
})

const getHeatColor = (count) => {
  if (count === 0) return 'var(--color-bg-hover)'
  if (count <= 1) return 'rgba(99, 102, 241, 0.2)'
  if (count <= 3) return 'rgba(99, 102, 241, 0.4)'
  if (count <= 5) return 'rgba(99, 102, 241, 0.6)'
  return 'rgba(99, 102, 241, 0.9)'
}

// 动态时间线
const timeline = computed(() => {
  return records.value.slice(0, 10).map(r => ({
    id: r.id,
    type: r.points_type,
    content: r.remark,
    change: r.change_value,
    time: r.create_time,
  }))
})

const getTimelineIcon = (type) => {
  if (type?.includes('发布')) return Document
  if (type?.includes('签到')) return Calendar
  if (type?.includes('点赞') || type?.includes('采纳')) return Star
  if (type?.includes('浏览')) return View
  return Flag
}

const getTimelineColor = (change) => {
  return change > 0 ? '#10B981' : '#EF4444'
}

const loadData = async () => {
  loading.value = true
  try {
    const [profileData, recordData, badgeData, knowledgeData, statsData] = await Promise.all([
      userApi.profile(),
      pointsApi.records({ page: 1, page_size: 100 }),
      growthApi.badges().catch(() => []),
      knowledgeApi.list({ mine: true, page: 1, page_size: 10 }).catch(() => ({ items: [] })),
      growthApi.stats().catch(() => null),
    ])
    profile.value = profileData
    records.value = recordData.items || []
    total.value = recordData.total || 0
    badges.value = badgeData || []
    myKnowledge.value = knowledgeData.items || []
    growthStats.value = statsData
    renderChart()
  } catch {} finally { loading.value = false }
}

const renderChart = async () => {
  await nextTick()
  if (!chartRef.value || !records.value.length) return
  const chart = echarts.init(chartRef.value)
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
  const textColor = isDark ? '#CBD5E1' : '#64748B'
  const gridLineColor = isDark ? 'rgba(255,255,255,0.06)' : '#f1f5f9'

  const sorted = [...records.value].reverse()
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: isDark ? 'rgba(30,41,59,0.95)' : 'rgba(255,255,255,0.95)',
      borderColor: isDark ? 'rgba(255,255,255,0.1)' : '#e2e8f0',
      textStyle: { color: isDark ? '#F1F5F9' : '#1e293b' },
      borderRadius: 12,
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map((r) => r.create_time?.slice(5, 10)),
      axisLine: { lineStyle: { color: gridLineColor } },
      axisLabel: { color: textColor },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: gridLineColor } },
      axisLabel: { color: textColor },
    },
    series: [{
      type: 'line',
      data: sorted.map((r) => r.after_points),
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 3, color: '#6366F1' },
      itemStyle: { color: '#6366F1' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(99,102,241,0.2)' },
          { offset: 1, color: 'rgba(99,102,241,0)' },
        ]),
      },
    }],
  })
  window.addEventListener('resize', () => chart.resize())
}

const handlePageChange = (p) => { page.value = p; loadData() }

onMounted(loadData)
</script>

<template>
  <div class="profile-page">
    <el-skeleton v-if="loading" :rows="8" animated />

    <template v-else>
      <!-- 用户信息卡片 -->
      <div class="profile-hero" v-if="profile">
        <div class="hero-bg">
          <div class="hero-orb hero-orb-1"></div>
          <div class="hero-orb hero-orb-2"></div>
        </div>
        <div class="hero-content">
          <div class="hero-left">
            <el-avatar :size="80" class="hero-avatar">
              {{ profile.real_name?.charAt(0) || 'U' }}
            </el-avatar>
            <div class="hero-info">
              <h1 class="hero-name">{{ profile.real_name }}</h1>
              <div class="hero-meta">
                <el-tag :type="profile.role === 'admin' ? 'danger' : 'primary'" effect="plain" size="small">
                  {{ profile.role === 'admin' ? '管理员' : '成员' }}
                </el-tag>
                <span class="hero-dept">{{ profile.department || '未设置部门' }}</span>
                <span class="hero-email">{{ profile.email || '' }}</span>
              </div>
              <div class="hero-level">
                <span class="level-badge-mini">Lv.{{ level }}</span>
                <span class="level-title">{{ levelTitle }}</span>
              </div>
            </div>
          </div>
          <div class="hero-stats">
            <div class="hero-stat">
              <div class="hero-stat-num">{{ profile.total_points }}</div>
              <div class="hero-stat-label">积分</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-num">{{ profile.total_contribution }}</div>
              <div class="hero-stat-label">贡献值</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-num">{{ profile.knowledge_count }}</div>
              <div class="hero-stat-label">知识数</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-num">{{ growthStats?.badge_count || 0 }}</div>
              <div class="hero-stat-label">勋章</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 勋章展示 -->
      <div class="page-card" v-if="badges.length">
        <div class="page-header">
          <h3 class="section-title">
            <el-icon style="margin-right: 6px; color: #F59E0B;"><Medal /></el-icon>
            我的勋章
          </h3>
          <span class="badge-count">{{ badges.length }} 枚</span>
        </div>
        <div class="badge-grid">
          <div v-for="badge in badges" :key="badge.id" class="badge-item hover-lift">
            <div class="badge-icon" :class="'rarity-' + (badge.rarity || 'common')">
              {{ badge.icon || '🏅' }}
            </div>
            <div class="badge-name">{{ badge.name }}</div>
            <div class="badge-desc">{{ badge.description }}</div>
          </div>
        </div>
      </div>

      <!-- 贡献热力图 -->
      <div class="page-card">
        <div class="page-header">
          <h3 class="section-title">
            <el-icon style="margin-right: 6px; color: #6366F1;"><Calendar /></el-icon>
            贡献热力图
          </h3>
          <span class="heatmap-total">共 {{ records.length }} 条记录</span>
        </div>
        <div class="heatmap-wrapper">
          <div class="heatmap-grid">
            <div v-for="(week, wi) in heatmapWeeks" :key="wi" class="heatmap-week">
              <div
                v-for="(day, di) in week"
                :key="di"
                class="heatmap-cell"
                :style="{ background: getHeatColor(day.count) }"
                :title="`${day.date}: ${day.count} 条记录`"
              />
            </div>
          </div>
          <div class="heatmap-legend">
            <span class="legend-label">少</span>
            <div class="legend-cell" style="background: var(--color-bg-hover)"></div>
            <div class="legend-cell" style="background: rgba(99, 102, 241, 0.2)"></div>
            <div class="legend-cell" style="background: rgba(99, 102, 241, 0.4)"></div>
            <div class="legend-cell" style="background: rgba(99, 102, 241, 0.6)"></div>
            <div class="legend-cell" style="background: rgba(99, 102, 241, 0.9)"></div>
            <span class="legend-label">多</span>
          </div>
        </div>
      </div>

      <!-- 成长曲线 + 动态时间线 -->
      <div class="profile-body">
        <div class="page-card" v-if="records.length">
          <div class="page-header">
            <h3 class="section-title">
              <el-icon style="margin-right: 6px; color: #3B82F6;"><TrendCharts /></el-icon>
              积分成长曲线
            </h3>
          </div>
          <div ref="chartRef" style="height: 280px"></div>
        </div>

        <!-- 最近动态时间线 -->
        <div class="page-card">
          <div class="page-header">
            <h3 class="section-title">
              <el-icon style="margin-right: 6px; color: #10B981;"><Clock /></el-icon>
              最近动态
            </h3>
          </div>
          <div class="activity-timeline">
            <div v-for="item in timeline" :key="item.id" class="timeline-item">
              <div class="timeline-dot" :style="{ background: getTimelineColor(item.change) }">
                <el-icon :size="12" color="#fff"><component :is="getTimelineIcon(item.type)" /></el-icon>
              </div>
              <div class="timeline-line"></div>
              <div class="timeline-content">
                <div class="timeline-text">{{ item.content }}</div>
                <div class="timeline-meta">
                  <span class="timeline-change" :class="item.change > 0 ? 'positive' : 'negative'">
                    {{ item.change > 0 ? '+' : '' }}{{ item.change }}
                  </span>
                  <span class="timeline-time">{{ item.time?.slice(5, 16) }}</span>
                </div>
              </div>
            </div>
            <div v-if="!timeline.length" class="empty-state">
              <div class="empty-state-icon">📝</div>
              <div class="empty-state-text">暂无动态记录</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 我的知识 -->
      <div class="page-card">
        <div class="page-header">
          <h3 class="section-title">
            <el-icon style="margin-right: 6px; color: #8B5CF6;"><Document /></el-icon>
            我的知识
          </h3>
          <span class="my-count">共 {{ profile?.knowledge_count || 0 }} 篇</span>
        </div>
        <div class="my-knowledge-grid">
          <div v-for="item in myKnowledge" :key="item.id" class="my-knowledge-item hover-lift">
            <div class="mk-header">
              <el-tag :type="item.status === 'approved' ? 'success' : item.status === 'pending' ? 'warning' : 'danger'" size="small" effect="plain">
                {{ item.status === 'approved' ? '已通过' : item.status === 'pending' ? '审核中' : '已驳回' }}
              </el-tag>
              <span class="mk-category">{{ item.category }}</span>
            </div>
            <h4 class="mk-title">{{ item.title }}</h4>
            <div class="mk-stats">
              <span><el-icon><View /></el-icon> {{ item.view_count }}</span>
              <span><el-icon><Star /></el-icon> {{ item.like_count }}</span>
              <span><el-icon><ChatDotRound /></el-icon> {{ item.comment_count }}</span>
            </div>
          </div>
          <div v-if="!myKnowledge.length" class="empty-state" style="grid-column: 1 / -1;">
            <div class="empty-state-icon">📚</div>
            <div class="empty-state-text">暂无知识，快去发布吧</div>
          </div>
        </div>
      </div>

      <!-- 积分流水 -->
      <div class="page-card">
        <div class="page-header">
          <h3 class="section-title">积分流水记录</h3>
        </div>
        <el-table :data="records" stripe style="border-radius: 12px;">
          <el-table-column prop="points_type" label="类型" min-width="140">
            <template #default="{ row }">
              <el-tag size="small" effect="plain">{{ row.points_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="change_value" label="变动" width="100">
            <template #default="{ row }">
              <span :style="{ color: row.change_value > 0 ? '#10b981' : '#ef4444', fontWeight: 700 }">
                {{ row.change_value > 0 ? '+' : '' }}{{ row.change_value }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="before_points" label="变动前" width="90" />
          <el-table-column prop="after_points" label="变动后" width="90" />
          <el-table-column prop="remark" label="说明" min-width="200" />
          <el-table-column prop="create_time" label="时间" width="170" />
        </el-table>
        <div style="display: flex; justify-content: flex-end; margin-top: 16px">
          <el-pagination
            v-model:current-page="page"
            :page-size="pageSize"
            :total="total"
            layout="total, prev, pager, next"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.profile-page { display: flex; flex-direction: column; gap: 20px; }
.section-title { font-size: 16px; font-weight: 600; color: var(--color-text-primary); margin: 0; display: flex; align-items: center; }

/* ---- Hero Card ---- */
.profile-hero {
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
  border-radius: 20px;
  padding: 32px;
  position: relative;
  overflow: hidden;
}
.hero-bg { position: absolute; inset: 0; pointer-events: none; }
.hero-orb { position: absolute; border-radius: 50%; filter: blur(80px); }
.hero-orb-1 { width: 300px; height: 300px; background: rgba(99,102,241,0.2); top: -100px; right: -50px; }
.hero-orb-2 { width: 200px; height: 200px; background: rgba(245,158,11,0.1); bottom: -80px; left: 20%; }
.hero-content { position: relative; z-index: 1; display: flex; align-items: center; justify-content: space-between; }
.hero-left { display: flex; align-items: center; gap: 20px; }
.hero-avatar { background: linear-gradient(135deg, #6366F1, #8B5CF6); color: #fff; font-size: 32px; font-weight: 700; }
.hero-name { color: #fff; font-size: 24px; font-weight: 700; margin-bottom: 8px; }
.hero-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.hero-dept, .hero-email { font-size: 13px; color: rgba(255,255,255,0.5); }
.hero-level { display: flex; align-items: center; gap: 8px; }
.level-badge-mini {
  padding: 2px 10px;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  border-radius: 6px;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}
.level-title { font-size: 13px; color: rgba(255,255,255,0.6); }
.hero-stats { display: flex; gap: 32px; }
.hero-stat { text-align: center; }
.hero-stat-num { font-size: 28px; font-weight: 800; color: #fff; }
.hero-stat-label { font-size: 12px; color: rgba(255,255,255,0.45); margin-top: 4px; }

/* ---- Badges ---- */
.badge-count { font-size: 13px; color: var(--color-text-secondary); }
.badge-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }
.badge-item {
  display: flex; flex-direction: column; align-items: center;
  padding: 16px 12px;
  background: var(--color-bg-hover);
  border-radius: 14px;
  text-align: center;
}
.badge-icon { font-size: 32px; margin-bottom: 8px; }
.badge-icon.rarity-legendary { filter: drop-shadow(0 0 8px rgba(245,158,11,0.5)); }
.badge-icon.rarity-epic { filter: drop-shadow(0 0 6px rgba(139,92,246,0.4)); }
.badge-icon.rarity-rare { filter: drop-shadow(0 0 4px rgba(59,130,246,0.3)); }
.badge-name { font-size: 13px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 4px; }
.badge-desc { font-size: 11px; color: var(--color-text-placeholder); line-height: 1.4; }

/* ---- Heatmap ---- */
.heatmap-total { font-size: 13px; color: var(--color-text-secondary); }
.heatmap-wrapper { overflow-x: auto; padding: 8px 0; }
.heatmap-grid { display: flex; gap: 3px; }
.heatmap-week { display: flex; flex-direction: column; gap: 3px; }
.heatmap-cell {
  width: 14px; height: 14px;
  border-radius: 3px;
  transition: all var(--transition-fast);
  cursor: pointer;
}
.heatmap-cell:hover { transform: scale(1.3); outline: 2px solid var(--color-primary); outline-offset: 1px; }
.heatmap-legend { display: flex; align-items: center; gap: 4px; margin-top: 10px; justify-content: flex-end; }
.legend-label { font-size: 11px; color: var(--color-text-placeholder); }
.legend-cell { width: 14px; height: 14px; border-radius: 3px; }

/* ---- Body Grid ---- */
.profile-body { display: grid; grid-template-columns: 1.5fr 1fr; gap: 20px; }

/* ---- Timeline ---- */
.activity-timeline { display: flex; flex-direction: column; gap: 0; }
.timeline-item { display: flex; gap: 14px; position: relative; padding-bottom: 20px; }
.timeline-item:last-child { padding-bottom: 0; }
.timeline-item:last-child .timeline-line { display: none; }
.timeline-dot {
  width: 28px; height: 28px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; z-index: 1;
}
.timeline-line {
  position: absolute;
  left: 13px; top: 28px; bottom: 0;
  width: 2px;
  background: var(--color-border);
}
.timeline-content { flex: 1; padding-top: 2px; }
.timeline-text { font-size: 13px; color: var(--color-text-regular); line-height: 1.5; margin-bottom: 4px; }
.timeline-meta { display: flex; align-items: center; gap: 10px; }
.timeline-change { font-size: 13px; font-weight: 700; }
.timeline-change.positive { color: #10B981; }
.timeline-change.negative { color: #EF4444; }
.timeline-time { font-size: 12px; color: var(--color-text-placeholder); }

/* ---- My Knowledge ---- */
.my-count { font-size: 13px; color: var(--color-text-secondary); }
.my-knowledge-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
.my-knowledge-item {
  padding: 16px;
  background: var(--color-bg-hover);
  border-radius: 14px;
  cursor: pointer;
}
.mk-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.mk-category { font-size: 11px; color: var(--color-text-placeholder); }
.mk-title { font-size: 14px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 8px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.mk-stats { display: flex; gap: 12px; font-size: 12px; color: var(--color-text-placeholder); }
.mk-stats span { display: flex; align-items: center; gap: 3px; }

@media (max-width: 1200px) {
  .profile-body { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .hero-content { flex-direction: column; gap: 20px; }
  .hero-left { flex-direction: column; text-align: center; }
  .hero-stats { gap: 20px; }
  .badge-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>
