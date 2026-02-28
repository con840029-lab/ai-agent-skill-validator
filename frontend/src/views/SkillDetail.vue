<template>
  <div class="skill-detail" v-loading="loading">
    <el-card v-if="skill">
      <template #header>
        <div class="card-header">
          <div>
            <h2>{{ skill.name }}</h2>
            <p style="margin: 8px 0 0; color: #666">{{ skill.description }}</p>
          </div>
          <el-button type="primary" @click="goBack">返回</el-button>
        </div>
      </template>

      <!-- Status -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-statistic title="状态" :value="getStatusText(skill.status)">
            <template #suffix>
              <el-tag :type="getStatusType(skill.status)" size="small">
                {{ getStatusText(skill.status) }}
              </el-tag>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="12">
          <el-statistic title="总得分" :value="skill.scores?.total?.toFixed(1) || '-'" suffix="分">
            <template #suffix>
              <span v-if="skill.scores?.total" class="score-badge" :class="getScoreClass(skill.scores.total)">
                {{ skill.scores.total.toFixed(1) }}
              </span>
            </template>
          </el-statistic>
        </el-col>
      </el-row>

      <!-- Report Tabs -->
      <el-tabs v-model="activeTab" style="margin-top: 30px">
        <el-tab-pane label="📊 评分概览" name="overview">
          <div v-if="skill.status === 'completed'">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card shadow="hover">
                  <template #header>🔧 技术评分 (50%)</template>
                  <div ref="techChartRef" style="height: 300px"></div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card shadow="hover">
                  <template #header>🤖 AI 表现评分 (50%)</template>
                  <div ref="aiChartRef" style="height: 300px"></div>
                </el-card>
              </el-col>
            </el-row>
          </div>
          <el-empty v-else description="评估尚未完成" />
        </el-tab-pane>

        <el-tab-pane label="📄 详细报告" name="report">
          <div v-if="skill.status === 'completed'">
            <el-radio-group v-model="reportFormat" style="margin-bottom: 20px">
              <el-radio-button label="html">HTML</el-radio-button>
              <el-radio-button label="markdown">Markdown</el-radio-button>
              <el-radio-button label="json">JSON</el-radio-button>
            </el-radio-group>

            <div v-if="reportFormat === 'html'" v-html="reportContent" class="report-content"></div>
            <div v-else-if="reportFormat === 'markdown'" class="report-content">
              <pre>{{ reportContent }}</pre>
            </div>
            <div v-else class="report-content">
              <pre>{{ JSON.stringify(reportContent, null, 2) }}</pre>
            </div>
          </div>
          <el-empty v-else description="评估尚未完成" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { skillAPI } from '../api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const skill = ref(null)
const activeTab = ref('overview')
const report = ref(null)
const reportFormat = ref('html')
const reportContent = ref('')
const techChartRef = ref(null)
const aiChartRef = ref(null)

const loadSkill = async () => {
  try {
    loading.value = true
    const response = await skillAPI.get(parseInt(route.params.id))
    skill.value = response.data
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const loadReport = async () => {
  if (skill.value?.status !== 'completed') return

  try {
    if (reportFormat.value === 'html') {
      const response = await skillAPI.getReportHtml(skill.value.id)
      reportContent.value = response.data
    } else if (reportFormat.value === 'markdown') {
      const response = await skillAPI.getReportMarkdown(skill.value.id)
      reportContent.value = response.data.markdown
    } else {
      const response = await skillAPI.getReportJson(skill.value.id)
      reportContent.value = response.data
    }
  } catch (error) {
    ElMessage.error('加载报告失败')
  }
}

const renderCharts = () => {
  if (!skill.value?.scores) return

  const techData = [
    { name: '工具能力', value: skill.value.scores.technical?.tool_capability || 0 },
    { name: '代码质量', value: skill.value.scores.technical?.code_quality || 0 },
    { name: '逻辑设计', value: skill.value.scores.technical?.logic || 0 },
    { name: 'RAG 能力', value: skill.value.scores.technical?.rag || 0 }
  ]

  const aiData = [
    { name: '任务达成', value: skill.value.scores.ai?.task_completion || 0 },
    { name: '指令遵循', value: skill.value.scores.ai?.instruction_following || 0 },
    { name: '抗干扰', value: skill.value.scores.ai?.robustness || 0 },
    { name: 'Token 效率', value: skill.value.scores.ai?.token_efficiency || 0 }
  ]

  if (techChartRef.value) {
    const techChart = echarts.init(techChartRef.value)
    techChart.setOption({
      radar: {
        indicator: [
          { name: '工具能力', max: 100 },
          { name: '代码质量', max: 100 },
          { name: '逻辑设计', max: 100 },
          { name: 'RAG 能力', max: 100 }
        ]
      },
      series: [{
        type: 'radar',
        data: [{
          value: techData.map(d => d.value),
          name: '技术评分',
          areaStyle: { color: 'rgba(102, 126, 234, 0.3)' },
          itemStyle: { color: '#667eea' }
        }]
      }]
    })
  }

  if (aiChartRef.value) {
    const aiChart = echarts.init(aiChartRef.value)
    aiChart.setOption({
      radar: {
        indicator: [
          { name: '任务达成', max: 100 },
          { name: '指令遵循', max: 100 },
          { name: '抗干扰', max: 100 },
          { name: 'Token 效率', max: 100 }
        ]
      },
      series: [{
        type: 'radar',
        data: [{
          value: aiData.map(d => d.value),
          name: 'AI 表现',
          areaStyle: { color: 'rgba(118, 75, 162, 0.3)' },
          itemStyle: { color: '#764ba2' }
        }]
      }]
    })
  }
}

watch(reportFormat, () => {
  loadReport()
})

watch(activeTab, (newTab) => {
  if (newTab === 'overview' && skill.value?.status === 'completed') {
    nextTick(() => {
      renderCharts()
    })
  } else if (newTab === 'report') {
    loadReport()
  }
})

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

const goBack = () => {
  router.push('/')
}

onMounted(async () => {
  await loadSkill()
  if (skill.value?.status === 'completed' && activeTab.value === 'overview') {
    nextTick(() => {
      renderCharts()
    })
  }
})
</script>

<style scoped>
.skill-detail {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-header h2 {
  margin: 0;
  color: #667eea;
}

.score-badge {
  font-size: 24px;
  font-weight: bold;
  padding: 4px 12px;
  border-radius: 8px;
}

.score-high {
  background: #f0f9ff;
  color: #67c23a;
}

.score-medium {
  background: #fef6e7;
  color: #e6a23c;
}

.score-low {
  background: #fef0f0;
  color: #f56c6c;
}

.report-content {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  max-height: 600px;
  overflow: auto;
}

.report-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
