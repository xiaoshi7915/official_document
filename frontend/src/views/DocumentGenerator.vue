<template>
  <div class="document-generator">
    <div class="container">
      <div class="generator-header">
        <h2>公文生成器</h2>
        <p>选择模板类型，填写相关信息，生成标准公文</p>
      </div>

      <el-row :gutter="20">
        <!-- 左侧：模板选择和表单 -->
        <el-col :span="16">
          <el-card class="form-card">
            <template #header>
              <div class="card-header">
                <span>公文信息</span>
                <el-button type="text" @click="uploadFile">
                  <el-icon><Upload /></el-icon>
                  上传文件
                </el-button>
              </div>
            </template>

            <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
              <!-- 模板选择 -->
              <el-form-item label="公文类型" prop="templateType">
                <el-select 
                  v-model="form.templateType" 
                  placeholder="请选择公文类型"
                  @change="onTemplateChange"
                  style="width: 100%"
                >
                  <el-option
                    v-for="template in templates"
                    :key="template.id"
                    :label="template.name"
                    :value="template.id"
                  >
                    <span>{{ template.name }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">
                      {{ template.description }}
                    </span>
                  </el-option>
                </el-select>
              </el-form-item>

              <!-- 基本信息 -->
              <el-form-item label="标题" prop="title">
                <el-input v-model="form.title" placeholder="请输入公文标题" />
              </el-form-item>

              <el-form-item label="发文机关" prop="sender">
                <el-input v-model="form.sender" placeholder="请输入发文机关名称" />
              </el-form-item>

              <el-form-item label="收文机关" prop="recipient">
                <el-input v-model="form.recipient" placeholder="请输入收文机关名称（可选）" />
              </el-form-item>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="文号" prop="documentNumber">
                    <el-input v-model="form.documentNumber" placeholder="如：京政发〔2025〕1号" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="发文日期" prop="date">
                    <el-date-picker
                      v-model="form.date"
                      type="date"
                      placeholder="选择日期"
                      format="YYYY年MM月DD日"
                      value-format="YYYY年MM月DD日"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="紧急程度">
                    <el-select v-model="form.urgencyLevel" placeholder="选择紧急程度">
                      <el-option label="特急" value="特急" />
                      <el-option label="急件" value="急件" />
                      <el-option label="一般" value="一般" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="密级">
                    <el-select v-model="form.securityLevel" placeholder="选择密级">
                      <el-option label="绝密" value="绝密" />
                      <el-option label="机密" value="机密" />
                      <el-option label="秘密" value="秘密" />
                      <el-option label="一般" value="一般" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <!-- 正文内容 -->
              <el-form-item label="正文内容" prop="content">
                <el-input
                  v-model="form.content"
                  type="textarea"
                  :rows="12"
                  placeholder="请输入公文正文内容，支持Markdown格式"
                />
              </el-form-item>

              <el-form-item label="输入格式">
                <el-radio-group v-model="form.formatType">
                  <el-radio label="markdown">Markdown</el-radio>
                  <el-radio label="plain">纯文本</el-radio>
                </el-radio-group>
              </el-form-item>

              <!-- 操作按钮 -->
              <el-form-item>
                <el-button type="primary" @click="generateDocument" :loading="generating">
                  <el-icon><Document /></el-icon>
                  生成公文
                </el-button>
                <el-button @click="resetForm">
                  <el-icon><Refresh /></el-icon>
                  重置
                </el-button>
                <el-button type="success" @click="previewDocument" :disabled="!form.templateType">
                  <el-icon><View /></el-icon>
                  预览模板
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <!-- 右侧：预览和帮助 -->
        <el-col :span="8">
          <el-card class="help-card">
            <template #header>
              <span>使用说明</span>
            </template>
            <div class="help-content">
              <h4>操作步骤：</h4>
              <ol>
                <li>选择合适的公文类型</li>
                <li>填写公文基本信息</li>
                <li>输入正文内容</li>
                <li>点击"生成公文"按钮</li>
                <li>下载生成的Word文档</li>
              </ol>

              <h4>格式说明：</h4>
              <ul>
                <li>支持Markdown语法</li>
                <li>自动处理段落格式</li>
                <li>符合GB/T9704-2012标准</li>
              </ul>

              <h4>Markdown示例：</h4>
              <pre class="markdown-example">
# 一级标题
## 二级标题

正文段落内容...

- 列表项1
- 列表项2
              </pre>
            </div>
          </el-card>

          <!-- 最近生成的文档 -->
          <el-card class="recent-card" v-if="recentDocuments.length > 0">
            <template #header>
              <span>最近生成</span>
            </template>
            <div class="recent-list">
              <div 
                v-for="doc in recentDocuments" 
                :key="doc.id"
                class="recent-item"
              >
                <div class="recent-info">
                  <div class="recent-title">{{ doc.title }}</div>
                  <div class="recent-time">{{ doc.createTime }}</div>
                </div>
                <el-button type="text" @click="downloadDocument(doc.downloadUrl)">
                  <el-icon><Download /></el-icon>
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 文件上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传文件" width="500px">
      <el-upload
        ref="uploadRef"
        :action="uploadUrl"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
        drag
        accept=".md,.docx,.doc,.txt"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 .md, .docx, .doc, .txt 格式文件
          </div>
        </template>
      </el-upload>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Document, Refresh, View, Download, UploadFilled } from '@element-plus/icons-vue'
import { getTemplates, generateDocument as generateDocumentApi, uploadFile as uploadFileApi } from '../api/document'

export default {
  name: 'DocumentGenerator',
  components: {
    Upload, Document, Refresh, View, Download, UploadFilled
  },
  setup() {
    const formRef = ref()
    const uploadRef = ref()
    const templates = ref([])
    const generating = ref(false)
    const uploadDialogVisible = ref(false)
    const recentDocuments = ref([])
    const uploadUrl = '/api/upload'

    const form = reactive({
      templateType: '',
      title: '',
      sender: '',
      recipient: '',
      documentNumber: '',
      date: '',
      urgencyLevel: '一般',
      securityLevel: '一般',
      content: '',
      formatType: 'markdown'
    })

    const rules = {
      templateType: [
        { required: true, message: '请选择公文类型', trigger: 'change' }
      ],
      title: [
        { required: true, message: '请输入标题', trigger: 'blur' }
      ],
      sender: [
        { required: true, message: '请输入发文机关', trigger: 'blur' }
      ],
      content: [
        { required: true, message: '请输入正文内容', trigger: 'blur' }
      ]
    }

    const loadTemplates = async () => {
      try {
        const response = await getTemplates()
        templates.value = response.data
      } catch (error) {
        ElMessage.error('加载模板失败')
      }
    }

    const onTemplateChange = (templateId) => {
      // 根据模板类型设置默认值或特殊处理
      console.log('选择模板:', templateId)
    }

    const generateDocument = async () => {
      console.log('点击生成公文按钮')
      if (!formRef.value) {
        console.error('表单引用不存在')
        ElMessage.error('表单引用不存在，请刷新页面重试')
        return
      }
      
      try {
        console.log('开始验证表单')
        const valid = await formRef.value.validate().catch(err => {
          console.error('表单验证失败:', err)
          return false
        })
        
        if (!valid) {
          console.error('表单验证未通过')
          ElMessage.error('请填写必填字段')
          return
        }
        
        console.log('表单验证通过')
        generating.value = true

        // 确保日期格式正确
        let formattedDate = form.date
        if (!formattedDate) {
          const now = new Date()
          formattedDate = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
        }

        const requestData = {
          content: form.content || '请在此处输入公文内容',
          template_type: form.templateType,
          metadata: {
            title: form.title,
            sender: form.sender,
            recipient: form.recipient || '',
            document_number: form.documentNumber || '',
            urgency_level: form.urgencyLevel || '一般',
            security_level: form.securityLevel || '一般',
            date: formattedDate,
            format_type: form.formatType || 'markdown'
          }
        }
        
        console.log('准备发送请求:', JSON.stringify(requestData))
        const response = await generateDocumentApi(requestData)
        console.log('收到响应:', response)
        
        if (response.data.success) {
          ElMessage.success('公文生成成功！')
          
          // 添加到最近生成列表
          recentDocuments.value.unshift({
            id: Date.now(),
            title: form.title,
            createTime: new Date().toLocaleString(),
            downloadUrl: response.data.download_url
          })

          // 自动下载
          downloadDocument(response.data.download_url)
        } else {
          ElMessage.error(response.data.message || '生成失败')
        }
      } catch (error) {
        console.error('生成文档失败:', error)
        ElMessage.error('生成文档失败，请检查输入信息')
      } finally {
        generating.value = false
      }
    }

    const resetForm = () => {
      if (formRef.value) {
        formRef.value.resetFields()
      }
    }

    const previewDocument = () => {
      if (form.templateType) {
        window.open(`/preview/${form.templateType}`, '_blank')
      }
    }

    const uploadFile = () => {
      uploadDialogVisible.value = true
    }

    const beforeUpload = (file) => {
      const validTypes = ['text/markdown', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'text/plain']
      const isValidType = validTypes.includes(file.type) || file.name.endsWith('.md')
      const isLt10M = file.size / 1024 / 1024 < 10

      if (!isValidType) {
        ElMessage.error('只支持 .md, .docx, .doc, .txt 格式文件!')
        return false
      }
      if (!isLt10M) {
        ElMessage.error('文件大小不能超过 10MB!')
        return false
      }
      return true
    }

    const handleUploadSuccess = (response) => {
      if (response.success) {
        form.content = response.content
        uploadDialogVisible.value = false
        ElMessage.success('文件上传成功！')
      } else {
        ElMessage.error('文件解析失败')
      }
    }

    const handleUploadError = () => {
      ElMessage.error('文件上传失败')
    }

    const downloadDocument = (downloadUrl) => {
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = ''
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }

    onMounted(() => {
      loadTemplates()
    })

    return {
      formRef,
      uploadRef,
      templates,
      form,
      rules,
      generating,
      uploadDialogVisible,
      recentDocuments,
      uploadUrl,
      onTemplateChange,
      generateDocument,
      resetForm,
      previewDocument,
      uploadFile,
      beforeUpload,
      handleUploadSuccess,
      handleUploadError,
      downloadDocument
    }
  }
}
</script>

<style scoped>
.document-generator {
  padding: 20px;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

.generator-header {
  text-align: center;
  margin-bottom: 30px;
}

.generator-header h2 {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 10px;
}

.generator-header p {
  color: #7f8c8d;
  font-size: 16px;
}

.form-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.help-card, .recent-card {
  margin-bottom: 20px;
}

.help-content h4 {
  color: #2c3e50;
  margin: 15px 0 10px 0;
  font-size: 14px;
}

.help-content ol, .help-content ul {
  margin: 0 0 15px 20px;
  font-size: 13px;
  color: #7f8c8d;
}

.help-content li {
  margin-bottom: 5px;
  line-height: 1.4;
}

.markdown-example {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  color: #495057;
  margin-top: 10px;
}

.recent-list {
  max-height: 200px;
  overflow-y: auto;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.recent-item:last-child {
  border-bottom: none;
}

.recent-info {
  flex: 1;
}

.recent-title {
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 4px;
}

.recent-time {
  font-size: 12px;
  color: #909399;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>