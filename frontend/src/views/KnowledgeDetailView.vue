<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import {
  View, Star, CollectionTag, ChatDotRound, Download,
  Share, ArrowLeft, User, Clock, Document, MagicStick,
  Promotion,
} from '@element-plus/icons-vue'
import { knowledgeApi } from '../api/modules'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const loading = ref(true)
const detail = ref(null)
const commentText = ref('')
const activeHeading = ref('')
const tocItems = ref([])

// 解析目录（从 content 中提取标题）
const parseToc = () => {
  if (!detail.value?.content) return
  const content = detail.value.content
  const headings = []
  const lines = content.split('\n')
  lines.forEach((line, idx) => {
    const match = line.match(/^(#{1,3})\s+(.+)/)
    if (match) {
      const level = match[1].length
      const text = match[2].trim()
      const id = 'heading-' + idx
      headings.push({ level, text, id })
    }
  })
  tocItems.value = headings
}

// 渲染内容（Markdown 简单渲染 + 添加 id）
const renderedContent = computed(() => {
  if (!detail.value?.content) return ''
  let content = detail.value.content
  // 给标题添加 id
  let idx = 0
  content = content.replace(/^(#{1,3})\s+(.+)$/gm, (match, hashes, text) => {
    const id = 'heading-' + idx++
    const level = hashes.length
    return `<h${level} id="${id}" class="content-heading">${text}</h${level}>`
  })
  // 基础 Markdown 渲染
  content = content
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code class="inline-code">$1</code>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>')
  return `<p>${content}</p>`
})

// 滚动监听
const handleScroll = () => {
  if (!tocItems.value.length) return
  for (let i = tocItems.value.length - 1; i >= 0; i--) {
    const el = document.getElementById(tocItems.value[i].id)
    if (el && el.getBoundingClientRect().top <= 120) {
      activeHeading.value = tocItems.value[i].id
      break
    }
  }
}

const scrollToHeading = (id) => {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// 互动操作
const doAction = async (action) => {
  if (!detail.value) return
  try {
    const res = await knowledgeApi.interact({ knowledge_id: detail.value.id, action })
    ElMessage.success(res.message || '操作成功')
    // 刷新详情
    const data = await knowledgeApi.detail(detail.value.id)
    Object.assign(detail.value, data)
  } catch {}
}

// 评论
const submitComment = async () => {
  if (!commentText.value.trim() || !detail.value) return
  try {
    await knowledgeApi.comment({ knowledge_id: detail.value.id, content: commentText.value })
    ElMessage.success('评论成功')
    commentText.value = ''
    const data = await knowledgeApi.detail(detail.value.id)
    Object.assign(detail.value, data)
  } catch {}
}

// 分享
const handleShare = () => {
  const url = window.location.href
  navigator.clipboard?.writeText(url).then(() => {
    ElMessage.success('链接已复制到剪贴板')
  }).catch(() => {
    ElMessage.info('请手动复制地址栏链接')
  })
}

// 热度评分
const heatScore = computed(() => {
  if (!detail.value) return 0
  const v = detail.value.view_count || 0
  const l = detail.value.like_count || 0
  const c = detail.value.comment_count || 0
  return Math.min(100, Math.round(v * 0.3 + l * 2 + c * 5))
})

const loadData = async () => {
  loading.value = true
  try {
    const id = route.params.id
    detail.value = await knowledgeApi.detail(id)
    parseToc()
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="detail-page">
    <!-- 返回按钮 -->
    <div class="detail-topbar">
      <button class="back-btn" @click="router.back()">
        <el-icon :size="18"><ArrowLeft /></el-icon>
        <span>返回</span>
      </button>
    </div>

    <el-skeleton v-if="loading" :rows="12" animated class="detail-skeleton" />

    <template v-else-if="detail">
      <div class="detail-layout">
        <!-- 左侧：目录 -->
        <aside class="detail-toc">
          <div class="toc-card glass-card-static">
            <h4 class="toc-title">目录</h4>
            <nav class="toc-nav">
              <div
                v-for="item in tocItems"
                :key="item.id"
                class="toc-item"
                :class="[
                  'toc-level-' + item.level,
                  { active: activeHeading === item.id }
                ]"
                @click="scrollToHeading(item.id)"
              >
                {{ item.text }}
              </div>
              <div v-if="!tocItems.length" class="toc-empty">暂无目录</div>
            </nav>
          </div>
        </aside>

        <!-- 中间：正文 -->
        <main class="detail-main">
          <div class="page-card detail-content-card">
            <!-- 文章头 -->
            <div class="article-header">
              <div class="article-meta-top">
                <el-tag type="primary" effect="plain" size="small">{{ detail.category }}</el-tag>
                <span class="meta-time"><el-icon><Clock /></el-icon> {{ detail.create_time }}</span>
              </div>
              <h1 class="article-title">{{ detail.title }}</h1>
              <p v-if="detail.summary" class="article-summary">{{ detail.summary }}</p>
              <div class="article-tags" v-if="detail.tags">
                <span v-for="tag in detail.tags.split(',')" :key="tag" class="tag-pill">{{ tag.trim() }}</span>
              </div>
            </div>

            <!-- 文章正文 -->
            <div class="article-body" v-html="renderedContent" />

            <!-- 互动栏 -->
            <div class="article-actions">
              <button class="action-btn" :class="{ active: detail.user_liked }" @click="doAction('like')">
                <el-icon><Star /></el-icon>
                <span>{{ detail.user_liked ? '已点赞' : '点赞' }} {{ detail.like_count }}</span>
              </button>
              <button class="action-btn" :class="{ active: detail.user_adopted }" @click="doAction('adopt')">
                <el-icon><CollectionTag /></el-icon>
                <span>{{ detail.user_adopted ? '已采纳' : '采纳' }} {{ detail.adopt_count }}</span>
              </button>
              <button class="action-btn" @click="doAction('view')">
                <el-icon><View /></el-icon>
                <span>浏览 {{ detail.view_count }}</span>
              </button>
              <button class="action-btn" @click="doAction('download')">
                <el-icon><Download /></el-icon>
                <span>下载 {{ detail.download_count }}</span>
              </button>
              <button class="action-btn share-btn" @click="handleShare">
                <el-icon><Share /></el-icon>
                <span>分享</span>
              </button>
            </div>

            <!-- 评论区 -->
            <div class="comment-section">
              <h3 class="comment-title">评论 ({{ detail.comments?.length || 0 }})</h3>
              <div class="comment-input">
                <el-input v-model="commentText" type="textarea" :rows="3" placeholder="写下你的评论..." resize="none" />
                <el-button type="primary" size="small" style="margin-top: 10px" @click="submitComment" :disabled="!commentText.trim()">发表评论</el-button>
              </div>
              <div class="comment-list">
                <div v-for="c in detail.comments" :key="c.id" class="comment-item">
                  <el-avatar :size="36" class="comment-avatar">{{ c.author_name?.charAt(0) }}</el-avatar>
                  <div class="comment-body">
                    <div class="comment-header">
                      <strong>{{ c.author_name }}</strong>
                      <span class="comment-time">{{ c.create_time }}</span>
                    </div>
                    <p class="comment-text">{{ c.content }}</p>
                  </div>
                </div>
                <div v-if="!detail.comments?.length" class="empty-state">
                  <div class="empty-state-icon">💬</div>
                  <div class="empty-state-text">暂无评论，快来发表第一条评论吧</div>
                </div>
              </div>
            </div>
          </div>
        </main>

        <!-- 右侧：信息栏 -->
        <aside class="detail-sidebar">
          <!-- 作者信息 -->
          <div class="sidebar-card glass-card-static">
            <div class="author-section">
              <el-avatar :size="48" class="author-avatar-lg">{{ detail.author_name?.charAt(0) || 'U' }}</el-avatar>
              <div class="author-info">
                <div class="author-name">{{ detail.author_name }}</div>
                <div class="author-role">知识贡献者</div>
              </div>
            </div>
          </div>

          <!-- 文章数据 -->
          <div class="sidebar-card glass-card-static">
            <h4 class="sidebar-title">文章数据</h4>
            <div class="data-grid">
              <div class="data-item">
                <div class="data-num">{{ detail.view_count || 0 }}</div>
                <div class="data-label">阅读量</div>
              </div>
              <div class="data-item">
                <div class="data-num">{{ detail.like_count || 0 }}</div>
                <div class="data-label">点赞数</div>
              </div>
              <div class="data-item">
                <div class="data-num">{{ detail.adopt_count || 0 }}</div>
                <div class="data-label">采纳数</div>
              </div>
              <div class="data-item">
                <div class="data-num">{{ detail.comment_count || 0 }}</div>
                <div class="data-label">评论数</div>
              </div>
            </div>
            <!-- 热度条 -->
            <div class="heat-bar">
              <div class="heat-label">
                <el-icon><Promotion /></el-icon>
                <span>热度评分</span>
                <span class="heat-value">{{ heatScore }}</span>
              </div>
              <el-progress :percentage="heatScore" :stroke-width="8" :show-text="false" :color="heatScore > 70 ? '#EF4444' : heatScore > 40 ? '#F59E0B' : '#10B981'" />
            </div>
          </div>

          <!-- AI 摘要 -->
          <div class="sidebar-card glass-card-static">
            <h4 class="sidebar-title">
              <el-icon style="margin-right: 4px; color: var(--color-primary);"><MagicStick /></el-icon>
              AI 摘要
            </h4>
            <p class="ai-summary">{{ detail.summary || '暂无 AI 摘要' }}</p>
          </div>

          <!-- 标签 -->
          <div class="sidebar-card glass-card-static" v-if="detail.tags">
            <h4 class="sidebar-title">标签</h4>
            <div class="sidebar-tags">
              <span v-for="tag in detail.tags.split(',')" :key="tag" class="tag-pill">{{ tag.trim() }}</span>
            </div>
          </div>
        </aside>
      </div>
    </template>

    <div v-else class="empty-state" style="padding: 80px 0;">
      <div class="empty-state-icon">📄</div>
      <div class="empty-state-text">文章不存在或已被删除</div>
      <el-button type="primary" @click="router.push('/app/knowledge')">返回知识库</el-button>
    </div>
  </div>
</template>

<style scoped>
.detail-page { display: flex; flex-direction: column; gap: 16px; }

/* ---- Top Bar ---- */
.detail-topbar { display: flex; align-items: center; }
.back-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 16px; border-radius: 10px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  font-size: 13px; font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-normal);
}
.back-btn:hover {
  color: var(--color-primary);
  border-color: var(--color-primary-lighter);
  background: var(--color-primary-bg);
}

/* ---- Three Column Layout ---- */
.detail-layout {
  display: grid;
  grid-template-columns: 220px 1fr 280px;
  gap: 20px;
  align-items: start;
}

/* ---- TOC ---- */
.detail-toc { position: sticky; top: 92px; }
.toc-card { padding: 20px; }
.toc-title { font-size: 14px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 12px; }
.toc-nav { display: flex; flex-direction: column; gap: 2px; }
.toc-item {
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  border-left: 2px solid transparent;
}
.toc-item:hover { color: var(--color-primary); background: var(--color-primary-bg); }
.toc-item.active { color: var(--color-primary); border-left-color: var(--color-primary); background: var(--color-primary-bg); font-weight: 600; }
.toc-level-2 { padding-left: 24px; font-size: 12px; }
.toc-level-3 { padding-left: 36px; font-size: 12px; }
.toc-empty { font-size: 12px; color: var(--color-text-placeholder); }

/* ---- Main Content ---- */
.detail-content-card { padding: 32px; }

.article-header { margin-bottom: 28px; padding-bottom: 20px; border-bottom: 1px solid var(--color-border-light); }
.article-meta-top { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.meta-time { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--color-text-placeholder); }
.article-title { font-size: 26px; font-weight: 700; color: var(--color-text-primary); line-height: 1.4; margin-bottom: 12px; letter-spacing: -0.5px; }
.article-summary { font-size: 14px; color: var(--color-text-secondary); line-height: 1.7; margin-bottom: 12px; }
.article-tags { display: flex; flex-wrap: wrap; gap: 6px; }

.article-body {
  font-size: 15px;
  color: var(--color-text-regular);
  line-height: 1.85;
  margin-bottom: 32px;
}
.article-body :deep(h1) { font-size: 22px; font-weight: 700; margin: 24px 0 12px; color: var(--color-text-primary); }
.article-body :deep(h2) { font-size: 18px; font-weight: 600; margin: 20px 0 10px; color: var(--color-text-primary); }
.article-body :deep(h3) { font-size: 16px; font-weight: 600; margin: 16px 0 8px; color: var(--color-text-primary); }
.article-body :deep(.inline-code) {
  background: var(--color-primary-bg);
  color: var(--color-primary);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

/* ---- Action Bar ---- */
.article-actions {
  display: flex;
  gap: 8px;
  padding: 16px 0;
  border-top: 1px solid var(--color-border-light);
  border-bottom: 1px solid var(--color-border-light);
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.action-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  font-size: 13px; font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-normal);
}
.action-btn:hover {
  background: var(--color-primary-bg);
  color: var(--color-primary);
  border-color: var(--color-primary-lighter);
}
.action-btn.active {
  background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1));
  color: var(--color-primary);
  border-color: rgba(99,102,241,0.3);
}
.share-btn:hover { color: #10B981; background: rgba(16,185,129,0.06); border-color: rgba(16,185,129,0.2); }

/* ---- Comments ---- */
.comment-section { margin-top: 8px; }
.comment-title { font-size: 16px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 16px; }
.comment-input { margin-bottom: 20px; }
.comment-list { display: flex; flex-direction: column; gap: 4px; }
.comment-item { display: flex; gap: 12px; padding: 14px 0; border-bottom: 1px solid var(--color-border-light); }
.comment-avatar { background: linear-gradient(135deg, #6366F1, #8B5CF6); color: #fff; font-size: 14px; flex-shrink: 0; }
.comment-body { flex: 1; }
.comment-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.comment-header strong { font-size: 14px; color: var(--color-text-primary); }
.comment-time { font-size: 12px; color: var(--color-text-placeholder); }
.comment-text { font-size: 14px; color: var(--color-text-regular); line-height: 1.6; }

/* ---- Right Sidebar ---- */
.detail-sidebar { display: flex; flex-direction: column; gap: 16px; position: sticky; top: 92px; }
.sidebar-card { padding: 20px; }
.sidebar-title { font-size: 14px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 12px; display: flex; align-items: center; }

.author-section { display: flex; align-items: center; gap: 12px; }
.author-avatar-lg { background: linear-gradient(135deg, #6366F1, #8B5CF6); color: #fff; font-weight: 700; font-size: 18px; }
.author-name { font-size: 15px; font-weight: 600; color: var(--color-text-primary); }
.author-role { font-size: 12px; color: var(--color-text-placeholder); margin-top: 2px; }

.data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.data-item { text-align: center; padding: 10px; background: var(--color-bg-hover); border-radius: 10px; }
.data-num { font-size: 20px; font-weight: 800; color: var(--color-text-primary); }
.data-label { font-size: 11px; color: var(--color-text-placeholder); margin-top: 2px; }

.heat-bar { display: flex; flex-direction: column; gap: 8px; }
.heat-label { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--color-text-secondary); }
.heat-value { margin-left: auto; font-weight: 700; color: var(--color-text-primary); }

.ai-summary {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.7;
  background: var(--color-bg-hover);
  padding: 12px;
  border-radius: 10px;
}

.sidebar-tags { display: flex; flex-wrap: wrap; gap: 6px; }

/* ---- Responsive ---- */
@media (max-width: 1200px) {
  .detail-layout { grid-template-columns: 1fr 260px; }
  .detail-toc { display: none; }
}
@media (max-width: 768px) {
  .detail-layout { grid-template-columns: 1fr; }
  .detail-sidebar { position: static; }
  .detail-content-card { padding: 20px; }
}
</style>
