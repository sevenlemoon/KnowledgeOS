<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import {
  View, Download, Star, CollectionTag, Search,
  ChatDotRound, Link, Clock, Document,
} from '@element-plus/icons-vue'
import { knowledgeApi, externalApi } from '../api/modules'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(6)

// 标签页：internal=内部知识 / external=外部知识源
const activeTab = ref('internal')

// 内部知识筛选
const query = reactive({
  keyword: '',
  category: '',
})

// 外部知识筛选
const externalTag = ref('')
const externalSource = ref('devto')
const externalTags = ref([])

const categories = [
  '开发经验', '需求分析', '测试技术', 'UI/UX', '数据分析', '项目管理', '架构设计', '安全运维',
  '运动健身', '健康饮食', '音乐艺术', '生活方式', '学习方法', '职场技能', '创意思维', '工具推荐',
]

// ---- 内部知识 ----
const loadList = async (p) => {
  if (p) page.value = p
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (query.keyword) params.keyword = query.keyword
    if (query.category) params.category = query.category
    const res = await knowledgeApi.list(params)
    list.value = res.items || []
    total.value = res.total || 0
  } catch {} finally { loading.value = false }
}

const handleSearch = () => { loadList(1) }
const handleCategoryChange = () => { loadList(1) }

// ---- 外部知识 ----
const externalList = ref([])
const externalTotal = ref(0)
const externalPage = ref(1)
const externalLoading = ref(false)

const loadExternal = async (p) => {
  if (p) externalPage.value = p
  externalLoading.value = true
  try {
    const params = { page: externalPage.value, page_size: 12, source: externalSource.value }
    if (externalTag.value) params.tag = externalTag.value
    const res = await externalApi.articles(params)
    externalList.value = res.items || []
    externalTotal.value = res.total || 0
  } catch {} finally { externalLoading.value = false }
}

const loadTags = async () => {
  try {
    const res = await externalApi.tags()
    externalTags.value = res || []
  } catch {}
}

const switchTab = (tab) => {
  activeTab.value = tab
  if (tab === 'external' && externalList.value.length === 0) {
    loadExternal(1)
  }
}

const switchSource = (src) => {
  externalSource.value = src
  loadExternal(1)
}

// 管理员删除知识
const handleDelete = async (id, title) => {
  try {
    await ElMessageBox.confirm(`确定要删除「${title}」吗？此操作不可恢复。`, '确认删除', { type: 'warning' })
    await knowledgeApi.delete(id)
    ElMessage.success('删除成功')
    loadList()
  } catch {}
}

// 互动操作
const doAction = async (id, action) => {
  try {
    const res = await knowledgeApi.interact({ knowledge_id: id, action })
    ElMessage.success(res.message || '操作成功')
    loadList()
  } catch {}
}

// 详情 - 跳转到详情页
const openDetail = (id) => {
  router.push(`/app/knowledge/${id}`)
}

// 外部链接跳转
const openExternalLink = (url) => {
  window.open(url, '_blank')
}

onMounted(() => {
  if (route.query.keyword) {
    query.keyword = route.query.keyword
  }
  loadList(1)
  loadTags()
})
</script>

<template>
  <div class="knowledge-page">
    <!-- 页面标题 -->
    <div class="page-header-section">
      <h2 class="page-title">知识库</h2>
      <p class="page-desc">内部知识沉淀 + 全球开发者社区精华</p>
    </div>

    <!-- 标签页切换 -->
    <div class="tab-switcher">
      <button :class="['tab-btn', { active: activeTab === 'internal' }]" @click="switchTab('internal')">
        内部知识
      </button>
      <button :class="['tab-btn', { active: activeTab === 'external' }]" @click="switchTab('external')">
        外部知识源
      </button>
    </div>

    <!-- ========== 内部知识 ========== -->
    <template v-if="activeTab === 'internal'">
      <!-- 搜索栏 -->
      <div class="filter-bar glass-card-static">
        <div class="search-box">
          <el-icon class="search-icon"><Search /></el-icon>
          <input v-model="query.keyword" class="search-input" placeholder="搜索知识标题、摘要..." @keyup.enter="handleSearch" />
        </div>
        <div class="category-filters">
          <el-button :type="!query.category ? 'primary' : ''" size="small" round @click="query.category = ''; handleCategoryChange()">全部</el-button>
          <el-button v-for="cat in categories" :key="cat" :type="query.category === cat ? 'primary' : ''" size="small" round @click="query.category = cat; handleCategoryChange()">{{ cat }}</el-button>
        </div>
      </div>

      <!-- 知识列表 -->
      <el-skeleton v-if="loading" :rows="4" animated />
      <template v-else>
        <div v-if="list.length" class="knowledge-grid">
          <div v-for="item in list" :key="item.id" class="knowledge-card glass-card" @click="openDetail(item.id)">
            <div class="card-header">
              <div class="card-category">{{ item.category }}</div>
              <div v-if="item.quality_score" class="quality-badge">{{ item.quality_score }}分</div>
            </div>
            <h3 class="card-title">{{ item.title }}</h3>
            <p class="card-summary">{{ item.summary }}</p>
            <div class="card-tags">
              <span v-for="tag in (item.tags || '').split(',')" :key="tag" class="tag-pill">{{ tag }}</span>
            </div>
            <div class="card-footer">
              <div class="card-stats">
                <span class="stat-item"><el-icon><View /></el-icon> {{ item.view_count }}</span>
                <span class="stat-item"><el-icon><Star /></el-icon> {{ item.like_count }}</span>
                <span class="stat-item"><el-icon><ChatDotRound /></el-icon> {{ item.comment_count }}</span>
              </div>
              <div class="card-actions">
                <span class="card-author">{{ item.author_name }}</span>
                <el-button v-if="authStore.isAdmin" type="danger" size="small" text @click.stop="handleDelete(item.id, item.title)">删除</el-button>
              </div>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无知识数据" />
      </template>

      <!-- 分页 -->
      <div v-if="total > 0" class="pagination-wrapper">
        <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadList" />
      </div>
    </template>

    <!-- ========== 外部知识源 ========== -->
    <template v-if="activeTab === 'external'">
      <!-- 来源切换 + 标签筛选 -->
      <div class="external-filter glass-card-static">
        <div class="source-switcher">
          <button :class="['source-btn', { active: externalSource === 'devto' }]" @click="switchSource('devto')">Dev.to</button>
          <button :class="['source-btn', { active: externalSource === 'github' }]" @click="switchSource('github')">GitHub</button>
          <button :class="['source-btn', { active: externalSource === 'bilibili' }]" @click="switchSource('bilibili')">Bilibili</button>
        </div>
        <div class="tag-filters" v-if="externalTags.length">
          <el-button :type="!externalTag ? 'primary' : ''" size="small" round @click="externalTag = ''; loadExternal(1)">全部</el-button>
          <el-button v-for="t in externalTags" :key="t.name" :type="externalTag === t.name ? 'primary' : ''" size="small" round @click="externalTag = t.name; loadExternal(1)">
            {{ t.label }}
          </el-button>
        </div>
      </div>

      <!-- 外部文章卡片（带图片） -->
      <el-skeleton v-if="externalLoading" :rows="6" animated />
      <template v-else>
        <div v-if="externalList.length" class="external-grid">
          <div v-for="item in externalList" :key="item.id" class="external-card glass-card" @click="openExternalLink(item.url)">
            <!-- 封面图 -->
            <div class="external-cover">
              <img v-if="item.cover_image" :src="item.source === 'Bilibili' ? `/api/external/image-proxy?url=${encodeURIComponent(item.cover_image)}` : item.cover_image" :alt="item.title" loading="lazy" />
              <div v-else class="cover-placeholder">
                <el-icon :size="32" color="#94a3b8"><Document /></el-icon>
              </div>
              <div class="source-badge">{{ item.source }}</div>
              <div v-if="item.video_duration" class="duration-badge">{{ item.video_duration }}</div>
            </div>
            <!-- 内容 -->
            <div class="external-body">
              <h3 class="external-title">{{ item.title }}</h3>
              <p class="external-summary">{{ item.summary }}</p>
              <div class="external-tags">
                <span v-for="tag in (item.tags || []).slice(0, 3)" :key="tag" class="tag-pill external-tag">{{ tag }}</span>
              </div>
              <div class="external-meta">
                <div class="meta-left">
                  <img v-if="item.author_avatar" :src="item.source === 'Bilibili' ? `/api/external/image-proxy?url=${encodeURIComponent(item.author_avatar)}` : item.author_avatar" class="author-avatar" />
                  <span class="author-name">{{ item.author }}</span>
                </div>
                <div class="meta-right">
                  <span v-if="item.source === 'Bilibili'"><el-icon><View /></el-icon> {{ item.reactions_count >= 10000 ? (item.reactions_count / 10000).toFixed(1) + '万' : item.reactions_count }}</span>
                  <span v-else><el-icon><Star /></el-icon> {{ item.reactions_count >= 1000 ? (item.reactions_count / 1000).toFixed(1) + 'k' : item.reactions_count }}</span>
                  <span v-if="item.source === 'GitHub'">Forks {{ item.forks || 0 }}</span>
                  <span v-if="item.source !== 'Bilibili' && item.reading_time"><el-icon><Clock /></el-icon> {{ item.reading_time }}min</span>
                  <span><el-icon><ChatDotRound /></el-icon> {{ item.comments_count }}</span>
                </div>
              </div>
            </div>
            <!-- 跳转提示 -->
            <div class="external-link-hint">
              <el-icon><Link /></el-icon> 查看原文
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无外部知识数据，请稍后重试" />
      </template>

      <!-- 外部分页 -->
      <div v-if="externalTotal > 0" class="pagination-wrapper">
        <el-pagination v-model:current-page="externalPage" :page-size="12" :total="externalTotal" layout="prev, pager, next" @current-change="loadExternal" />
      </div>
    </template>
  </div>
</template>

<style scoped>
.knowledge-page { display: flex; flex-direction: column; gap: 20px; }
.page-header-section { margin-bottom: 4px; }
.page-title { font-size: 22px; font-weight: 700; color: var(--color-text-primary); margin-bottom: 4px; }
.page-desc { font-size: 13px; color: var(--color-text-secondary); }

/* ---- Tab Switcher ---- */
.tab-switcher { display: flex; gap: 4px; background: var(--color-bg-hover); border-radius: 12px; padding: 4px; width: fit-content; }
.tab-btn {
  padding: 8px 20px; border-radius: 10px; border: none; cursor: pointer;
  font-size: 14px; font-weight: 500; color: var(--color-text-secondary); background: transparent;
  transition: all 0.2s;
}
.tab-btn.active { background: var(--color-bg-card); color: var(--color-primary); box-shadow: var(--shadow-sm); font-weight: 600; }

/* ---- Filter Bar ---- */
.filter-bar { display: flex; flex-direction: column; gap: 14px; padding: 16px 20px; }
.search-box { display: flex; align-items: center; gap: 8px; background: var(--color-bg-hover); border-radius: 10px; padding: 8px 14px; }
.search-icon { color: var(--color-text-placeholder); }
.search-input { flex: 1; border: none; outline: none; background: transparent; font-size: 14px; color: var(--color-text-primary); }
.category-filters { display: flex; flex-wrap: wrap; gap: 6px; }

/* ---- Internal Knowledge Grid ---- */
.knowledge-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
.knowledge-card {
  padding: 20px; cursor: pointer; transition: all 0.25s ease; position: relative;
}
.knowledge-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-card-hover); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.card-category { font-size: 11px; color: var(--color-primary); background: var(--color-primary-bg); padding: 3px 10px; border-radius: 6px; font-weight: 600; }
.quality-badge {
  font-size: 11px; color: #f59e0b; background: rgba(245,158,11,0.1); padding: 3px 8px; border-radius: 6px; font-weight: 700;
}
.card-title { font-size: 15px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 8px; line-height: 1.4; }
.card-summary { font-size: 13px; color: var(--color-text-secondary); line-height: 1.6; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 12px; }
.tag-pill { font-size: 11px; color: var(--color-primary); background: var(--color-primary-bg); padding: 2px 8px; border-radius: 4px; }
.card-footer { display: flex; justify-content: space-between; align-items: center; }
.card-actions { display: flex; align-items: center; gap: 8px; }
.card-stats { display: flex; gap: 12px; }
.stat-item { display: flex; align-items: center; gap: 3px; font-size: 12px; color: var(--color-text-placeholder); }
.card-author { font-size: 12px; color: var(--color-text-secondary); font-weight: 500; }

/* ---- External Knowledge ---- */
.external-filter { display: flex; flex-direction: column; gap: 14px; padding: 16px 20px; }
.source-switcher { display: flex; gap: 8px; }
.source-btn {
  padding: 6px 16px; border-radius: 8px; border: 1px solid var(--color-border); cursor: pointer;
  font-size: 13px; color: var(--color-text-secondary); background: var(--color-bg-card); transition: all 0.2s;
}
.source-btn.active { border-color: var(--color-primary); color: var(--color-primary); background: var(--color-primary-bg); font-weight: 600; }
.tag-filters { display: flex; flex-wrap: wrap; gap: 6px; }

.external-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.external-card {
  padding: 0; overflow: hidden; cursor: pointer; transition: all 0.25s ease;
  display: flex; flex-direction: column;
}
.external-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-card-hover); }

.external-cover { position: relative; height: 180px; overflow: hidden; background: var(--color-bg-hover); }
.external-cover img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.external-card:hover .external-cover img { transform: scale(1.05); }
.cover-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: var(--color-bg-hover); }
.source-badge {
  position: absolute; top: 10px; right: 10px;
  padding: 3px 10px; border-radius: 6px;
  font-size: 11px; font-weight: 600; color: #fff;
  background: rgba(0,0,0,0.5); backdrop-filter: blur(8px);
}
.duration-badge {
  position: absolute; bottom: 10px; right: 10px;
  padding: 2px 8px; border-radius: 4px;
  font-size: 11px; font-weight: 600; color: #fff;
  background: rgba(0,0,0,0.7);
}

.external-body { padding: 16px; flex: 1; display: flex; flex-direction: column; }
.external-title { font-size: 14px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 8px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.external-summary { font-size: 12px; color: var(--color-text-secondary); line-height: 1.6; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.external-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 10px; }
.external-tag { font-size: 10px; }
.external-meta { display: flex; justify-content: space-between; align-items: center; margin-top: auto; }
.meta-left { display: flex; align-items: center; gap: 6px; }
.author-avatar { width: 22px; height: 22px; border-radius: 50%; }
.author-name { font-size: 12px; color: var(--color-text-regular); font-weight: 500; }
.meta-right { display: flex; gap: 10px; font-size: 11px; color: var(--color-text-placeholder); }
.meta-right span { display: flex; align-items: center; gap: 2px; }

.external-link-hint {
  padding: 8px 16px; border-top: 1px solid var(--color-border-light);
  font-size: 12px; color: var(--color-primary); display: flex; align-items: center; gap: 4px;
  transition: background 0.2s;
}
.external-card:hover .external-link-hint { background: var(--color-primary-bg); }

/* ---- Pagination ---- */
.pagination-wrapper { display: flex; justify-content: center; padding: 16px 0; }

</style>
