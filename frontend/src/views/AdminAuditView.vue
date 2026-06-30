<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Close, Setting, Document, TrendCharts } from '@element-plus/icons-vue'
import { adminApi } from '../api/modules'

const pendingList = ref([])
const configs = ref([])
const auditHistory = ref([])
const dialogVisible = ref(false)
const currentRow = ref(null)
const auditForm = reactive({
  knowledge_id: null,
  status: 'approved',
  quality_score: 85,
  remark: '',
})

const loadData = async () => {
  try {
    const [pendingData, configData, historyData] = await Promise.all([
      adminApi.pendingKnowledge(),
      adminApi.getConfig(),
      adminApi.auditHistory(),
    ])
    pendingList.value = pendingData || []
    configs.value = configData || []
    auditHistory.value = historyData || []
  } catch {}
}

const openAudit = (row, status) => {
  currentRow.value = row
  auditForm.knowledge_id = row.id
  auditForm.status = status
  auditForm.quality_score = status === 'approved' ? 85 : 0
  auditForm.remark = ''
  dialogVisible.value = true
}

const submitAudit = async () => {
  try {
    await adminApi.auditKnowledge(auditForm)
    ElMessage.success('审核完成')
    dialogVisible.value = false
    // 重新加载待审核列表和审核历史
    const [pendingData, historyData] = await Promise.all([
      adminApi.pendingKnowledge(),
      adminApi.auditHistory(),
    ])
    pendingList.value = pendingData || []
    auditHistory.value = historyData || []
  } catch {}
}

const saveConfig = async () => {
  try {
    const payload = {}
    configs.value.forEach((item) => { payload[item.config_key] = item.config_value })
    await adminApi.updateConfig(payload)
    ElMessage.success('参数已更新')
  } catch {}
}

onMounted(loadData)
</script>

<template>
  <div class="admin-page">
    <!-- 统计卡片 -->
    <div class="stat-row">
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #fef3c7, #fde68a)">
          <el-icon :size="20" style="color: #f59e0b"><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">待审核</div>
          <div class="stat-value">{{ pendingList.length }}</div>
        </div>
      </div>
    </div>

    <!-- 审核列表 -->
    <div class="page-card">
      <div class="page-header">
        <h2 class="page-title"><el-icon style="margin-right: 8px"><Check /></el-icon>知识审核</h2>
      </div>
      <div v-if="pendingList.length" class="audit-list">
        <div
          v-for="(item, idx) in pendingList"
          :key="item.id"
          class="audit-card"
          :style="{ animationDelay: `${idx * 0.06}s` }"
        >
          <div class="audit-content">
            <div class="audit-header">
              <h3 class="audit-title">{{ item.title }}</h3>
              <el-tag type="warning" size="small" effect="plain">{{ item.category }}</el-tag>
            </div>
            <p class="audit-summary">{{ item.summary }}</p>
            <div class="audit-meta">
              <el-avatar :size="24" class="meta-avatar">{{ item.author_name?.charAt(0) || 'U' }}</el-avatar>
              <span class="meta-author">{{ item.author_name }}</span>
              <span class="meta-time">{{ item.create_time }}</span>
            </div>
          </div>
          <div class="audit-actions">
            <el-button type="success" :icon="Check" @click="openAudit(item, 'approved')">通过</el-button>
            <el-button type="danger" :icon="Close" @click="openAudit(item, 'rejected')">驳回</el-button>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无待审核知识" />
    </div>

    <!-- 积分配置 -->
    <div class="page-card">
      <div class="page-header">
        <h2 class="page-title"><el-icon style="margin-right: 8px"><Setting /></el-icon>激励参数配置</h2>
        <el-button type="primary" @click="saveConfig">保存配置</el-button>
      </div>
      <el-table :data="configs" stripe>
        <el-table-column prop="config_key" label="参数键" width="220">
          <template #default="{ row }">
            <el-tag effect="plain" type="info">{{ row.config_key }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="260" />
        <el-table-column label="参数值" width="160">
          <template #default="{ row }">
            <el-input v-model="row.config_value" size="small" />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 审核历史 -->
    <div class="page-card">
      <div class="page-header">
        <h2 class="page-title"><el-icon style="margin-right: 8px"><TrendCharts /></el-icon>审核历史</h2>
      </div>
      <el-table :data="auditHistory" stripe v-if="auditHistory.length">
        <el-table-column prop="knowledge_title" label="知识标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="auditor_name" label="审核人" width="100" />
        <el-table-column prop="status" label="审核结果" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'approved' ? 'success' : 'danger'" size="small" effect="plain">
              {{ row.status === 'approved' ? '通过' : '驳回' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quality_score" label="质量分" width="80" />
        <el-table-column prop="remark" label="审核意见" min-width="180" show-overflow-tooltip />
        <el-table-column prop="create_time" label="时间" width="170" />
      </el-table>
      <el-empty v-else description="暂无审核记录" :image-size="60" />
    </div>

    <!-- 审核弹窗 -->
    <el-dialog v-model="dialogVisible" title="知识审核" width="520px" class="audit-dialog">
      <template v-if="currentRow">
        <div class="dialog-preview">
          <h4>{{ currentRow.title }}</h4>
          <p>{{ currentRow.summary }}</p>
        </div>
      </template>
      <el-form :model="auditForm" label-position="top">
        <el-form-item label="审核结果">
          <el-radio-group v-model="auditForm.status">
            <el-radio value="approved">
              <el-tag type="success" effect="plain">通过</el-tag>
            </el-radio>
            <el-radio value="rejected">
              <el-tag type="danger" effect="plain">驳回</el-tag>
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="auditForm.status === 'approved'" label="质量评分 (0-100)">
          <el-slider v-model="auditForm.quality_score" :min="0" :max="100" :step="5" show-input />
        </el-form-item>
        <el-form-item label="审核意见">
          <el-input v-model="auditForm.remark" type="textarea" :rows="4" placeholder="请输入审核意见..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAudit">确认提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.admin-page { display: flex; flex-direction: column; gap: 20px; }

.stat-row { display: flex; gap: 16px; }
.stat-card {
  background: var(--color-bg-card);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border-light);
  min-width: 200px;
}
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.stat-label { font-size: 13px; color: var(--color-text-secondary); }
.stat-value { font-size: 24px; font-weight: 800; color: var(--color-text-primary); }

/* ---- Audit List ---- */
.audit-list { display: flex; flex-direction: column; gap: 12px; }
.audit-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border: 1px solid var(--color-border-light);
  border-radius: 14px;
  transition: all 0.25s ease;
  animation: fadeInUp 0.4s ease both;
}
.audit-card:hover { box-shadow: var(--shadow-md); border-color: var(--color-primary-lightest); }

.audit-content { flex: 1; }
.audit-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.audit-title { font-size: 16px; font-weight: 600; color: var(--color-text-primary); margin: 0; }
.audit-summary { font-size: 13px; color: var(--color-text-secondary); margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.audit-meta { display: flex; align-items: center; gap: 8px; }
.meta-avatar { background: linear-gradient(135deg, #3b82f6, #6366f1); color: #fff; font-size: 12px; font-weight: 600; }
.meta-author { font-size: 13px; font-weight: 500; color: var(--color-text-regular); }
.meta-time { font-size: 12px; color: var(--color-text-placeholder); }

.audit-actions { display: flex; gap: 8px; flex-shrink: 0; margin-left: 20px; }

/* ---- Dialog ---- */
.dialog-preview {
  background: var(--color-bg-hover);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}
.dialog-preview h4 { font-size: 15px; font-weight: 600; margin-bottom: 6px; color: var(--color-text-primary); }
.dialog-preview p { font-size: 13px; color: var(--color-text-secondary); }

@media (max-width: 768px) {
  .audit-card { flex-direction: column; gap: 16px; }
  .audit-actions { margin-left: 0; }
}
</style>
