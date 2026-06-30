<script setup>
import { onMounted, ref } from 'vue'
import { Trophy } from '@element-plus/icons-vue'
import { pointsApi } from '../api/modules'

const ranking = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const loadData = async (p) => {
  if (p) page.value = p
  loading.value = true
  try {
    const res = await pointsApi.ranking({ page: page.value, page_size: pageSize.value })
    ranking.value = res.items || []
    total.value = res.total || 0
  } catch {} finally { loading.value = false }
}

const getRankClass = (idx) => {
  const globalIdx = (page.value - 1) * pageSize.value + idx
  if (globalIdx === 0) return 'rank-gold'
  if (globalIdx === 1) return 'rank-silver'
  if (globalIdx === 2) return 'rank-bronze'
  return ''
}

const getRankIcon = (idx) => {
  const globalIdx = (page.value - 1) * pageSize.value + idx
  if (globalIdx === 0) return '🥇'
  if (globalIdx === 1) return '🥈'
  if (globalIdx === 2) return '🥉'
  return globalIdx + 1
}

onMounted(loadData)
</script>

<template>
  <div class="ranking-page">
    <div class="page-card">
      <div class="page-header">
        <h2 class="page-title"><el-icon style="margin-right: 8px"><Trophy /></el-icon>积分排行榜</h2>
      </div>

      <!-- 前三名展示 -->
      <div v-if="ranking.length >= 3 && page === 1" class="top-three">
        <div class="top-item top-2">
          <div class="top-medal">🥈</div>
          <el-avatar :size="56" class="top-avatar">{{ ranking[1].real_name?.charAt(0) }}</el-avatar>
          <div class="top-name">{{ ranking[1].real_name }}</div>
          <div class="top-dept">{{ ranking[1].department || '未设置' }}</div>
          <div class="top-points">{{ ranking[1].total_points }} 积分</div>
        </div>
        <div class="top-item top-1">
          <div class="top-medal">🥇</div>
          <el-avatar :size="72" class="top-avatar">{{ ranking[0].real_name?.charAt(0) }}</el-avatar>
          <div class="top-name">{{ ranking[0].real_name }}</div>
          <div class="top-dept">{{ ranking[0].department || '未设置' }}</div>
          <div class="top-points">{{ ranking[0].total_points }} 积分</div>
        </div>
        <div class="top-item top-3">
          <div class="top-medal">🥉</div>
          <el-avatar :size="56" class="top-avatar">{{ ranking[2].real_name?.charAt(0) }}</el-avatar>
          <div class="top-name">{{ ranking[2].real_name }}</div>
          <div class="top-dept">{{ ranking[2].department || '未设置' }}</div>
          <div class="top-points">{{ ranking[2].total_points }} 积分</div>
        </div>
      </div>

      <!-- 排行列表 -->
      <div class="ranking-list" v-loading="loading">
        <div
          v-for="(item, idx) in ranking"
          :key="item.user_id"
          class="ranking-row"
          :class="getRankClass(idx)"
          :style="{ animationDelay: `${idx * 0.04}s` }"
        >
          <div class="row-rank">
            <span v-if="typeof getRankIcon(idx) === 'string'" class="rank-icon-text">{{ getRankIcon(idx) }}</span>
            <span v-else class="rank-num">{{ getRankIcon(idx) }}</span>
          </div>
          <el-avatar :size="40" class="row-avatar">{{ item.real_name?.charAt(0) || 'U' }}</el-avatar>
          <div class="row-info">
            <div class="row-name">{{ item.real_name }}</div>
            <div class="row-dept">{{ item.department || '未设置部门' }}</div>
          </div>
          <div class="row-score">
            <div class="score-main">{{ item.total_points }}</div>
            <div class="score-sub">贡献度 {{ item.total_contribution }}</div>
          </div>
        </div>
        <el-empty v-if="!ranking.length && !loading" description="暂无排行数据" />
      </div>

      <!-- 分页 -->
      <div style="display: flex; justify-content: flex-end; margin-top: 16px">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadData"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.ranking-page { display: flex; flex-direction: column; gap: 20px; }

/* ---- Top Three ---- */
.top-three { display: flex; align-items: flex-end; justify-content: center; gap: 24px; margin-bottom: 32px; padding: 24px 0; }
.top-item { display: flex; flex-direction: column; align-items: center; text-align: center; }
.top-medal { font-size: 36px; margin-bottom: 8px; }
.top-avatar { background: linear-gradient(135deg, #3b82f6, #6366f1); color: #fff; font-weight: 700; font-size: 24px; margin-bottom: 8px; }
.top-1 .top-avatar { width: 72px; height: 72px; font-size: 28px; }
.top-2 .top-avatar, .top-3 .top-avatar { width: 56px; height: 56px; }
.top-name { font-size: 16px; font-weight: 700; color: var(--color-text-primary); margin-bottom: 4px; }
.top-dept { font-size: 12px; color: var(--color-text-secondary); margin-bottom: 6px; }
.top-points { font-size: 18px; font-weight: 800; color: var(--color-primary); }
.top-1 { order: 1; transform: translateY(-16px); }
.top-2 { order: 0; }
.top-3 { order: 2; }

/* ---- Ranking List ---- */
.ranking-list { display: flex; flex-direction: column; gap: 8px; }
.ranking-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 20px;
  border-radius: 14px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  transition: all 0.25s ease;
  animation: fadeInUp 0.4s ease both;
}
.ranking-row:hover { transform: translateX(4px); box-shadow: var(--shadow-md); }

.rank-gold { background: linear-gradient(135deg, rgba(245,158,11,0.12), rgba(251,191,36,0.06)); border-color: rgba(245,158,11,0.3); }
.rank-silver { background: linear-gradient(135deg, rgba(148,163,184,0.12), rgba(203,213,225,0.06)); border-color: rgba(148,163,184,0.3); }
.rank-bronze { background: linear-gradient(135deg, rgba(217,119,6,0.12), rgba(245,158,11,0.06)); border-color: rgba(217,119,6,0.3); }

.row-rank { width: 40px; text-align: center; }
.rank-icon-text { font-size: 24px; }
.rank-num { font-size: 16px; font-weight: 700; color: var(--color-text-secondary); }

.row-avatar { background: linear-gradient(135deg, #3b82f6, #6366f1); color: #fff; font-weight: 600; font-size: 16px; flex-shrink: 0; }
.row-info { flex: 1; }
.row-name { font-size: 15px; font-weight: 600; color: var(--color-text-primary); }
.row-dept { font-size: 12px; color: var(--color-text-secondary); margin-top: 2px; }

.row-score { text-align: right; }
.score-main { font-size: 20px; font-weight: 800; color: var(--color-primary); }
.score-sub { font-size: 12px; color: var(--color-text-secondary); margin-top: 2px; }
</style>
