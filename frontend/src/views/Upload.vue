<template>
  <div class="upload-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>📤 上传 Skill</h2>
          <el-button type="text" @click="goBack">返回列表</el-button>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="Skill 名称" prop="name">
          <el-input v-model="form.name" placeholder="例如: 天气查询 Skill" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="简要描述这个 Skill 的功能"
          />
        </el-form-item>
        
        <el-form-item label="Skill 包" prop="file" required>
          <el-upload
            ref="uploadRef"
            drag
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            accept=".zip,.tar.gz"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                仅支持 .zip 或 .tar.gz 格式，文件大小不超过 100MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            开始评估
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="uploadResult" style="margin-top: 20px">
      <template #header>
        <span>📊 评估结果</span>
      </template>
      <el-result
        icon="success"
        title="上传成功"
        :sub-title="uploadResult.message"
      >
        <template #extra>
          <el-button type="primary" @click="viewResult">查看详情</el-button>
        </template>
      </el-result>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { skillAPI } from '../api'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref()
const uploadRef = ref()
const loading = ref(false)
const uploadResult = ref(null)

const form = reactive({
  name: '',
  description: '',
  file: null
})

const rules = {
  name: [{ required: true, message: '请输入 Skill 名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入描述', trigger: 'blur' }]
}

const handleFileChange = (file) => {
  const maxSize = 100 * 1024 * 1024 // 100MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 100MB')
    return
  }
  
  const allowedTypes = ['application/zip', 'application/x-tar', 'application/gzip']
  const fileName = file.name.toLowerCase()
  
  if (!fileName.endsWith('.zip') && !fileName.endsWith('.tar.gz')) {
    ElMessage.error('仅支持 .zip 或 .tar.gz 格式')
    return
  }
  
  form.file = file
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const handleSubmit = async () => {
  if (!form.file) {
    ElMessage.error('请选择文件')
    return
  }

  try {
    await formRef.value.validate()
    loading.value = true

    const formData = new FormData()
    formData.append('file', form.file.raw)
    formData.append('name', form.name)
    formData.append('description', form.description)

    const response = await skillAPI.upload(formData)
    uploadResult.value = response.data
    ElMessage.success('上传成功，评估已开始')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '上传失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formRef.value?.resetFields()
  form.file = null
  uploadRef.value?.clearFiles()
  uploadResult.value = null
}

const goBack = () => {
  router.push('/')
}

const viewResult = () => {
  if (uploadResult.value) {
    router.push(`/skill/${uploadResult.value.id}`)
  }
}
</script>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #667eea;
}

:deep(.el-upload-dragger) {
  padding: 40px;
}
</style>
