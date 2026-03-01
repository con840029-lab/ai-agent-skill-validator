<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="header-card">
          <div class="header-content">
            <div>
              <h2>🎯 我的 Skills</h2>
              <p>管理和评估您的 AI Agent Skills</p>
            </div>
            <el-button type="primary" @click="goToUpload" :icon="Upload">
              上传 Skill
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="6">
        <el-statistic title="总 Skill 数" :value="stats.total" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="已完成评估" :value="stats.completed" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="评估中" :value="stats.pending" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="平均得分" :value="stats.avgScore" :precision="1" suffix="分" />
      </el-col>
    </el-row>

    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Skill 列表</span>
              <el-button type="text" @click="loadSkills" :icon="Refresh">刷新</el-button>
            </div>
          </template>

          <el-table :data="skills" v-loading="loading" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="name" label="名称" width="200" />
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
            <el-table-column label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="得分" width="100">
              <template #default="{ row }">
                <span v-if="row.total_score > 0" :class="getScoreClass(row.total_score)">
                  {{ row.total_score.toFixed(1) }}
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="viewSkill(row.id)">
                  查看
                </el-button>
                <el-button type="danger" link @click="deleteSkill(row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-if="total > 0"
            style="margin-top: 20px; justify-content: flex-end"
            :current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="total, prev, pager, next"
            @current-change="handlePageChange"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { skillAPI } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Refresh } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const skills = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const stats = computed(() => {
  return {
    total: total.value,
    completed: skills.value.filter(s => s.status === 'completed').length,
    pending: skills.value.filter(s => s.status === 'pending' || s.status === 'analyzing').length,
    avgScore: skills.value.length > 0
      ? skills.value.filter(s => s.total_score > 0).reduce((sum, s) => sum + s.total_score, 0) / skills.value.filter(s => s.total_score > 0).length
      : 0
  }
})

const loadSkills = async () => {
  try {
    loading.value = true
    const response = await skillAPI.list({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    })
    skills.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadSkills()
}

const goToUpload = () => {
  router.push('/upload')
}

const viewSkill = (id) => {
  router.push(`/skill/${id}`)
}

const deleteSkill = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个 Skill 吗？', '确认删除', {
      type: 'warning'
    })
    
    await skillAPI.delete(id)
    ElMessage.success('删除成功')
    loadSkills()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const getStatusType = (status) => {
  const types = {
    pending: 'info',
    analyzing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '等待中',
    analyzing: '评估中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

const getScoreClass = (score) => {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-medium'
  return 'score-low'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadSkills()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.header-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0 0 8px 0;
}

.header-content p {
  margin: 0;
  opacity: 0.9;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-high {
  color: #67c23a;
  font-weight: bold;
}

.score-medium {
  color: #e6a23c;
  font-weight: bold;
}

.score-low {
  color: #f56c6c;
  font-weight: bold;
}
</style>
