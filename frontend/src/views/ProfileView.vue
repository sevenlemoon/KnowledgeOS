<script setup>
import * as echarts from 'echarts'
import { nextTick, onMounted, ref } from 'vue'
import { Trophy, Document, TrendCharts, Medal } from '@element-plus/icons-vue'
import { pointsApi, userApi } from '../api/modules'

const profile = ref(null)
const records = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const chartRef = ref(null)

const loadData = async () => {
  try {
    const [profileData, recordData] = await Promise.all([
      userApi.profile(),
      pointsApi.records({ page: page.value, page_size: pageSize.value }),
    ])
    profile.value = profileData
    records.value = recordData.items || []
    total.value = recordData.total || 0
    renderChart()
  } catch {}
}

const renderChart = async () => {
  await nextTick()
  if (!chartRef.value || !records.value.length) return
  const chart = echarts.init(chartRef.value)
  const sorted = [...records.value].reverse()
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map((r) => r.create_time?.slice(5, 10)),
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#94a3b8' },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#94a3b8' },
    },
    series: [{
      type: 'line',
      data: sorted.map((r) => r.after_points),
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: { width: 3, color: '#3b82f6' },
      itemStyle: { color: '#3b82f6' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(59,130,246,0.2)' },
          { offset: 1, color: 'rgba(59,130,246,0)' },
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
    <!-- 用户信息卡片 -->
    <div class="profile-header page-card" v-if="profile">
      <div class="profile-avatar-section">
        <el-avatar :size="80" class="profile-avatar">
          {{ profile.real_name?.charAt(0) || 'U' }}
        </el-avatar>
        <div class="profile-basic">
          <h2 class="profile-name">{{ profile.real_name }}</h2>
          <div class="profile-meta">
            <el-tag :type="profile.role === 'admin' ? 'danger' : 'primary'" effect="plain">
              {{ profile.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
            <span class="meta-text">{{ profile.department || '未设置部门' }}</span>
            <span class="meta-text">{{ profile.email || '未设置邮箱' }}</span>
          </div>
        </div>
      </div>
      <div class="profile-stats">
        <div class="profile-stat">
          <el-icon :size="20" style="color: #f59e0b"><Trophy /></el-icon>
          <div class="stat-num">{{ profile.total_points }}</div>
          <div class="stat-label">累计积分</div>
        </div>
        <div class="profile-stat">
          <el-icon :size="20" style="color: #10b981"><TrendCharts /></el-icon>
          <div class="stat-num">{{ profile.total_contribution }}</div>
          <div class="stat-label">贡献度</div>
        </div>
        <div class="profile-stat">
          <el-icon :size="20" style="color: #3b82f6"><Document /></el-icon>
          <div class="stat-num">{{ profile.knowledge_count }}</div>
          <div class="stat-label">知识总数</div>
        </div>
        <div class="profile-stat">
          <el-icon :size="20" style="color: #6366f1"><Medal /></el-icon>
          <div class="stat-num">{{ profile.approved_knowledge_count }}</div>
          <div class="stat-label">审核通过</div>
        </div>
      </div>
    </div>

    <!-- 成长曲线 -->
    <div class="page-card" v-if="records.length">
      <div class="page-header">
        <h3 class="section-title">积分成长曲线</h3>
      </div>
      <div ref="chartRef" style="height: 280px"></div>
    </div>

    <!-- 积分流水 -->
    <div class="page-card">
      <div class="page-header">
        <h3 class="section-title">积分流水记录</h3>
      </div>
      <el-table :data="records" stripe>
        <el-table-column prop="points_type" label="积分类型" min-width="140">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.points_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="change_value" label="变动值" width="100">
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
  </div>
</template>

<style scoped>
.profile-page { display: flex; flex-direction: column; gap: 20px; }
.section-title { font-size: 16px; font-weight: 600; color: var(--color-text-primary); margin: 0; }

.profile-header { display: flex; align-items: center; justify-content: space-between; }
.profile-avatar-section { display: flex; align-items: center; gap: 20px; }
.profile-avatar { background: linear-gradient(135deg, #3b82f6, #6366f1); color: #fff; font-size: 32px; font-weight: 700; }
.profile-name { font-size: 22px; font-weight: 700; color: var(--color-text-primary); margin-bottom: 8px; }
.profile-meta { display: flex; align-items: center; gap: 12px; }
.meta-text { font-size: 14px; color: var(--color-text-secondary); }

.profile-stats { display: flex; gap: 32px; }
.profile-stat { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.stat-num { font-size: 22px; font-weight: 800; color: var(--color-text-primary); }
.stat-label { font-size: 12px; color: var(--color-text-secondary); }

@media (max-width: 768px) {
  .profile-header { flex-direction: column; gap: 20px; }
  .profile-stats { gap: 20px; }
}
</style>
