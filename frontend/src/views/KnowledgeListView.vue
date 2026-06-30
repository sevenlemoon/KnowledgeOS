<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import {
  View, Download, Star, CollectionTag, Search,
  ChatDotRound, Link, Clock, Document,
} from '@element-plus/icons-vue'
import { knowledgeApi, externalApi } from '../api/modules'

const route = useRoute()
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

// 详情
const detailVisible = ref(false)
const detail = ref(null)
const commentText = ref('')
const openDetail = async (id) => {
  try {
    detail.value = await knowledgeApi.detail(id)
    detailVisible.value = true
    loadList()
  } catch {}
}
const submitComment = async () => {
  if (!commentText.value.trim()) return
  try {
    await knowledgeApi.comment({ knowledge_id: detail.value.id, content: commentText.value })
    ElMessage.success('评论成功')
    commentText.value = ''
    openDetail(detail.value.id)
    loadList()
  } catch {}
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

    <!-- ========== 详情抽屉 ========== -->
    <el-drawer v-model="detailVisible" :title="detail?.title" size="50%" direction="rtl">
      <template v-if="detail">
        <div class="detail-meta">
          <el-tag>{{ detail.category }}</el-tag>
          <span class="meta-author">{{ detail.author_name }}</span>
          <span class="meta-time">{{ detail.create_time }}</span>
        </div>
        <div class="detail-content" v-html="detail.content?.replace(/\n/g, '<br/>')" />
        <div class="detail-stats">
          <div class="detail-stat" @click="doAction(detail.id, 'view')"><el-icon><View /></el-icon> 浏览 {{ detail.view_count }}</div>
          <div class="detail-stat" @click="doAction(detail.id, 'download')"><el-icon><Download /></el-icon> 下载 {{ detail.download_count }}</div>
          <div class="detail-stat" :class="{ 'stat-active': detail.user_liked }" @click="doAction(detail.id, 'like')"><el-icon><Star /></el-icon> {{ detail.user_liked ? '已点赞' : '点赞' }} {{ detail.like_count }}</div>
          <div class="detail-stat" :class="{ 'stat-active': detail.user_adopted }" @click="doAction(detail.id, 'adopt')"><el-icon><CollectionTag /></el-icon> {{ detail.user_adopted ? '已采纳' : '采纳' }} {{ detail.adopt_count }}</div>
        </div>
        <div class="comment-section">
          <h4>评论 ({{ detail.comments?.length || 0 }})</h4>
          <div class="comment-input">
            <el-input v-model="commentText" type="textarea" :rows="2" placeholder="发表评论..." />
            <el-button type="primary" size="small" style="margin-top: 8px" @click="submitComment">提交评论</el-button>
          </div>
          <div v-for="c in detail.comments" :key="c.id" class="comment-item">
            <el-avatar :size="32" class="comment-avatar">{{ c.author_name?.charAt(0) }}</el-avatar>
            <div class="comment-body">
              <div class="comment-header"><strong>{{ c.author_name }}</strong><span>{{ c.create_time }}</span></div>
              <p>{{ c.content }}</p>
            </div>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<style scoped>
.knowledge-page { display: flex; flex-direction: column; gap: 20px; }
.page-header-section { margin-bottom: 4px; }
.page-title { font-size: 22px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
.page-desc { font-size: 13px; color: #64748b; }

/* ---- Tab Switcher ---- */
.tab-switcher { display: flex; gap: 4px; background: rgba(0,0,0,0.04); border-radius: 12px; padding: 4px; width: fit-content; }
.tab-btn {
  padding: 8px 20px; border-radius: 10px; border: none; cursor: pointer;
  font-size: 14px; font-weight: 500; color: #64748b; background: transparent;
  transition: all 0.2s;
}
.tab-btn.active { background: #fff; color: #6366f1; box-shadow: 0 1px 4px rgba(0,0,0,0.08); font-weight: 600; }

/* ---- Filter Bar ---- */
.filter-bar { display: flex; flex-direction: column; gap: 14px; padding: 16px 20px; }
.search-box { display: flex; align-items: center; gap: 8px; background: #f1f5f9; border-radius: 10px; padding: 8px 14px; }
.search-icon { color: #94a3b8; }
.search-input { flex: 1; border: none; outline: none; background: transparent; font-size: 14px; color: #1e293b; }
.category-filters { display: flex; flex-wrap: wrap; gap: 6px; }

/* ---- Internal Knowledge Grid ---- */
.knowledge-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
.knowledge-card {
  padding: 20px; cursor: pointer; transition: all 0.25s ease; position: relative;
}
.knowledge-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.1); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.card-category { font-size: 11px; color: #6366f1; background: rgba(99,102,241,0.08); padding: 3px 10px; border-radius: 6px; font-weight: 600; }
.quality-badge {
  font-size: 11px; color: #f59e0b; background: rgba(245,158,11,0.1); padding: 3px 8px; border-radius: 6px; font-weight: 700;
}
.card-title { font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 8px; line-height: 1.4; }
.card-summary { font-size: 13px; color: #64748b; line-height: 1.6; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 12px; }
.tag-pill { font-size: 11px; color: #6366f1; background: rgba(99,102,241,0.06); padding: 2px 8px; border-radius: 4px; }
.card-footer { display: flex; justify-content: space-between; align-items: center; }
.card-actions { display: flex; align-items: center; gap: 8px; }
.card-stats { display: flex; gap: 12px; }
.stat-item { display: flex; align-items: center; gap: 3px; font-size: 12px; color: #94a3b8; }
.card-author { font-size: 12px; color: #64748b; font-weight: 500; }

/* ---- External Knowledge ---- */
.external-filter { display: flex; flex-direction: column; gap: 14px; padding: 16px 20px; }
.source-switcher { display: flex; gap: 8px; }
.source-btn {
  padding: 6px 16px; border-radius: 8px; border: 1px solid #e2e8f0; cursor: pointer;
  font-size: 13px; color: #64748b; background: #fff; transition: all 0.2s;
}
.source-btn.active { border-color: #6366f1; color: #6366f1; background: rgba(99,102,241,0.04); font-weight: 600; }
.tag-filters { display: flex; flex-wrap: wrap; gap: 6px; }

.external-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.external-card {
  padding: 0; overflow: hidden; cursor: pointer; transition: all 0.25s ease;
  display: flex; flex-direction: column;
}
.external-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.12); }

.external-cover { position: relative; height: 180px; overflow: hidden; background: #f1f5f9; }
.external-cover img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.external-card:hover .external-cover img { transform: scale(1.05); }
.cover-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #f1f5f9, #e2e8f0); }
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
.external-title { font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 8px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.external-summary { font-size: 12px; color: #64748b; line-height: 1.6; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.external-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 10px; }
.external-tag { font-size: 10px; }
.external-meta { display: flex; justify-content: space-between; align-items: center; margin-top: auto; }
.meta-left { display: flex; align-items: center; gap: 6px; }
.author-avatar { width: 22px; height: 22px; border-radius: 50%; }
.author-name { font-size: 12px; color: #475569; font-weight: 500; }
.meta-right { display: flex; gap: 10px; font-size: 11px; color: #94a3b8; }
.meta-right span { display: flex; align-items: center; gap: 2px; }

.external-link-hint {
  padding: 8px 16px; border-top: 1px solid rgba(0,0,0,0.04);
  font-size: 12px; color: #6366f1; display: flex; align-items: center; gap: 4px;
  transition: background 0.2s;
}
.external-card:hover .external-link-hint { background: rgba(99,102,241,0.04); }

/* ---- Pagination ---- */
.pagination-wrapper { display: flex; justify-content: center; padding: 16px 0; }

/* ---- Detail Drawer ---- */
.detail-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.meta-author { font-size: 13px; color: #475569; font-weight: 500; }
.meta-time { font-size: 12px; color: #94a3b8; }
.detail-content { font-size: 14px; color: #334155; line-height: 1.8; margin-bottom: 24px; }
.detail-stats { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
.detail-stat {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 16px; border-radius: 10px;
  font-size: 13px; color: #475569; background: #f8fafc;
  border: 1px solid #e2e8f0; cursor: pointer;
  transition: all 0.2s;
}
.detail-stat:hover { background: rgba(99,102,241,0.06); color: #6366f1; border-color: rgba(99,102,241,0.2); }
.stat-active { background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1)) !important; color: #6366f1 !important; border-color: rgba(99,102,241,0.3) !important; }
.comment-section h4 { font-size: 15px; font-weight: 600; margin-bottom: 12px; }
.comment-input { margin-bottom: 16px; }
.comment-item { display: flex; gap: 10px; padding: 12px 0; border-bottom: 1px solid #f1f5f9; }
.comment-avatar { background: linear-gradient(135deg, #6366F1, #8B5CF6); color: #fff; font-size: 13px; flex-shrink: 0; }
.comment-body { flex: 1; }
.comment-header { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; }
.comment-header strong { color: #1e293b; }
.comment-header span { color: #94a3b8; font-size: 12px; }
.comment-body p { font-size: 13px; color: #475569; line-height: 1.6; }
</style>
