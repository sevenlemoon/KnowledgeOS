<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { EditPen, Collection, PriceTag, Document } from '@element-plus/icons-vue'
import { knowledgeApi } from '../api/modules'

const loading = ref(false)
const currentStep = ref(0)
const form = reactive({
  title: '',
  summary: '',
  category: '开发经验',
  tags: '',
  content: '',
})

const categories = [
  '开发经验', '需求分析', '测试技术', 'UI/UX', '数据分析', '项目管理', '架构设计', '安全运维',
  '运动健身', '健康饮食', '音乐艺术', '生活方式', '学习方法', '职场技能', '创意思维', '工具推荐'
]

const submit = async () => {
  if (!form.title || !form.summary || !form.content) {
    ElMessage.warning('请填写必填项')
    return
  }
  loading.value = true
  try {
    await knowledgeApi.add(form)
    ElMessage.success('提交成功，等待管理员审核')
    form.title = ''
    form.summary = ''
    form.category = '开发经验'
    form.tags = ''
    form.content = ''
    currentStep.value = 0
  } catch {} finally { loading.value = false }
}
</script>

<template>
  <div class="publish-page">
    <!-- 步骤条 -->
    <div class="page-card">
      <el-steps :active="currentStep" finish-status="success" align-center class="publish-steps">
        <el-step title="基本信息" :icon="Document" description="标题与摘要" />
        <el-step title="分类标签" :icon="Collection" description="选择分类" />
        <el-step title="知识内容" :icon="EditPen" description="详细内容" />
        <el-step title="提交审核" :icon="PriceTag" description="确认发布" />
      </el-steps>
    </div>

    <!-- 表单内容 -->
    <div class="page-card publish-form">
      <!-- Step 1: 基本信息 -->
      <div v-show="currentStep === 0">
        <h3 class="step-title">基本信息</h3>
        <el-form label-position="top">
          <el-form-item label="知识标题" required>
            <el-input v-model="form.title" placeholder="请输入知识标题，建议简洁明了" size="large" maxlength="200" show-word-limit />
          </el-form-item>
          <el-form-item label="知识摘要" required>
            <el-input v-model="form.summary" type="textarea" :rows="4" placeholder="请简要描述知识的核心内容，帮助他人快速了解" maxlength="500" show-word-limit />
          </el-form-item>
        </el-form>
      </div>

      <!-- Step 2: 分类标签 -->
      <div v-show="currentStep === 1">
        <h3 class="step-title">分类与标签</h3>
        <el-form label-position="top">
          <el-form-item label="知识分类" required>
            <div class="category-grid">
              <div
                v-for="cat in categories"
                :key="cat"
                class="category-item"
                :class="{ active: form.category === cat }"
                @click="form.category = cat"
              >
                {{ cat }}
              </div>
            </div>
          </el-form-item>
          <el-form-item label="标签（选填，逗号分隔）">
            <el-input v-model="form.tags" placeholder="例如：Vue3, FastAPI, MySQL" size="large" />
          </el-form-item>
        </el-form>
      </div>

      <!-- Step 3: 内容 -->
      <div v-show="currentStep === 2">
        <h3 class="step-title">知识内容</h3>
        <el-form label-position="top">
          <el-form-item label="详细内容" required>
            <el-input v-model="form.content" type="textarea" :rows="16" placeholder="请详细描述知识内容、实现步骤、关键代码、注意事项等..." />
          </el-form-item>
        </el-form>
      </div>

      <!-- Step 4: 确认 -->
      <div v-show="currentStep === 3">
        <h3 class="step-title">确认发布</h3>
        <div class="preview-card">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="标题">{{ form.title || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="摘要">{{ form.summary || '未填写' }}</el-descriptions-item>
            <el-descriptions-item label="分类">{{ form.category }}</el-descriptions-item>
            <el-descriptions-item label="标签">{{ form.tags || '无' }}</el-descriptions-item>
            <el-descriptions-item label="内容预览">
              <div class="content-preview">{{ form.content || '未填写' }}</div>
            </el-descriptions-item>
          </el-descriptions>
        </div>
        <el-alert type="info" :closable="false" show-icon style="margin-top: 16px">
          提交后将进入审核流程，管理员审核通过后其他用户即可查看。
        </el-alert>
      </div>

      <!-- 操作按钮 -->
      <div class="step-actions">
        <el-button v-if="currentStep > 0" @click="currentStep--">上一步</el-button>
        <div style="flex:1"></div>
        <el-button v-if="currentStep < 3" type="primary" @click="currentStep++">下一步</el-button>
        <el-button v-if="currentStep === 3" type="primary" :loading="loading" @click="submit">
          {{ loading ? '提交中...' : '提交审核' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.publish-page { display: flex; flex-direction: column; gap: 20px; }

.publish-steps { padding: 8px 0; }
.step-title { font-size: 18px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 24px; }

.category-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.category-item {
  padding: 14px 16px;
  border: 2px solid var(--color-border);
  border-radius: 12px;
  text-align: center;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-regular);
  cursor: pointer;
  transition: all 0.25s ease;
}
.category-item:hover { border-color: var(--color-primary-lighter); color: var(--color-primary); }
.category-item.active {
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
  color: var(--color-primary);
  font-weight: 600;
}

.preview-card { margin-bottom: 16px; }
.content-preview { max-height: 200px; overflow-y: auto; white-space: pre-wrap; line-height: 1.6; font-size: 13px; color: var(--color-text-secondary); }

.step-actions { display: flex; align-items: center; margin-top: 32px; padding-top: 20px; border-top: 1px solid var(--color-border-light); }

@media (max-width: 768px) {
  .category-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
