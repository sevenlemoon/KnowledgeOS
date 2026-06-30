<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Refresh } from '@element-plus/icons-vue'
import { userApi } from '../api/modules'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const users = ref([])

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await userApi.list()
    users.value = res.items || []
  } catch {} finally { loading.value = false }
}

const handleDelete = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定删除用户「${user.real_name}」吗？删除后该用户的所有知识、积分、评论将一并清除，且无法恢复。`,
      '确认删除',
      { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' }
    )
    await userApi.delete(user.id)
    ElMessage.success('删除成功')
    loadUsers()
  } catch {}
}

onMounted(loadUsers)
</script>

<template>
  <div class="user-manage">
    <div class="page-header-section">
      <h2 class="page-title">用户管理</h2>
      <p class="page-desc">管理系统用户，查看用户信息和知识贡献</p>
    </div>

    <div class="page-card">
      <div class="card-header-bar">
        <span class="total-text">共 {{ users.length }} 个用户</span>
        <el-button :icon="Refresh" circle size="small" @click="loadUsers" />
      </div>

      <el-skeleton v-if="loading" :rows="6" animated />
      <el-table v-else :data="users" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名" width="100" />
        <el-table-column prop="role" label="角色" width="80">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : ''" size="small" effect="plain">
              {{ row.role === 'admin' ? '管理员' : '成员' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="160" />
        <el-table-column prop="total_points" label="积分" width="80" sortable />
        <el-table-column prop="knowledge_count" label="知识数" width="80" sortable />
        <el-table-column prop="create_time" label="注册时间" width="150" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.id !== authStore.user?.id && row.role !== 'admin'"
              type="danger"
              size="small"
              text
              :icon="Delete"
              @click="handleDelete(row)"
            >删除</el-button>
            <span v-else-if="row.id === authStore.user?.id" class="text-muted">当前用户</span>
            <span v-else class="text-muted">管理员</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.user-manage { display: flex; flex-direction: column; gap: 20px; }
.page-header-section { margin-bottom: 4px; }
.page-title { font-size: 22px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
.page-desc { font-size: 13px; color: #64748b; }
.card-header-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.total-text { font-size: 13px; color: #64748b; }
.text-muted { font-size: 12px; color: #94a3b8; }
</style>
