<template>
  <div class="document-generator">
    <div class="container">
      <div class="generator-header">
        <h2>公文生成智能体</h2>
        <p>选择模板类型，填写相关信息，生成标准公文</p>
      </div>

      <!-- 使用说明 -->
      <el-card class="help-card-top">
        <template #header>
          <span>使用说明</span>
        </template>
        <div class="help-content">
          <div class="help-section">
            <h4>操作步骤：</h4>
            <ol>
              <li>选择合适的公文类型</li>
              <li>填写公文基本信息</li>
              <li>输入正文内容</li>
              <li>点击"生成公文"按钮</li>
              <li>下载生成的Word文档</li>
            </ol>
          </div>

          <div class="help-section">
            <h4>格式说明：</h4>
            <ul>
              <li>支持Markdown语法</li>
              <li>自动处理段落格式</li>
              <li>符合GB/T9704-2012标准</li>
            </ul>
          </div>

          <div class="help-section">
            <h4>Markdown示例：</h4>
            <pre class="markdown-example">
      # 一级标题
      ## 二级标题

      正文段落内容...

      - 列表项1
      - 列表项2
    </pre>
          </div>
        </div>
      </el-card>

      <el-row :gutter="20">
        <!-- 左侧：模板选择和表单 -->
        <el-col :span="12">
          <el-card class="form-card">
            <template #header>
              <div class="card-header">
                <span>公文信息</span>
                <el-button link @click="uploadFile">
                  <el-icon>
                    <Upload />
                  </el-icon>
                  上传文件
                </el-button>
              </div>
            </template>

            <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
              <!-- 模板选择 -->
              <el-form-item label="公文类型" prop="templateType">
                <el-select v-model="form.templateType" placeholder="请选择公文类型" @change="onTemplateChange"
                  style="width: 100%">
                  <el-option v-for="template in templates" :key="template.id" :label="template.name"
                    :value="template.id">
                    <span>{{ template.name }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">
                      {{ template.description }}
                    </span>
                  </el-option>
                </el-select>
              </el-form-item>

              <!-- 公文字段折叠面板 -->
              <el-collapse v-model="activeCollapse">
                <!-- 版头 -->
                <el-collapse-item title="版头" name="header">
                  <el-form-item label="份号" prop="copyNumber">
                    <el-input v-model="form.copyNumber" placeholder="请输入份号" />
                  </el-form-item>

                  <!-- 密级和保密期限 -->
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="密级" prop="securityLevel">
                        <el-select v-model="form.securityLevel" placeholder="选择密级">
                          <el-option label="绝密" value="绝密" />
                          <el-option label="机密" value="机密" />
                          <el-option label="秘密" value="秘密" />
                          <el-option label="一般" value="一般" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="保密期限" prop="securityPeriod">
                        <el-input v-model="form.securityPeriod" placeholder="请输入保密期限" />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-form-item label="紧急程度" prop="urgencyLevel">
                    <el-select v-model="form.urgencyLevel" placeholder="选择紧急程度">
                      <el-option label="特急" value="特急" />
                      <el-option label="急件" value="急件" />
                      <el-option label="一般" value="一般" />
                    </el-select>
                  </el-form-item>

                  <!-- 发文机关标志 -->
                  <el-form-item label="发文机关名称" prop="sender">
                    <el-input v-model="form.sender" placeholder="请输入发文机关名称" />
                  </el-form-item>

                  <el-form-item label="标志" prop="senderSymbol">
                    <el-input v-model="form.senderSymbol" placeholder="请输入标志" />
                  </el-form-item>

                  <!-- 发文字号 -->
                  <el-row :gutter="20">
                    <el-col :span="8">
                      <el-form-item label="发文机关代字" prop="senderCode">
                        <el-input v-model="form.senderCode" placeholder="如：京政发" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="年份" prop="year">
                        <el-input v-model="form.year" placeholder="如：2025" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="发文顺序号" prop="serialNumber">
                        <el-input v-model="form.serialNumber" placeholder="如：1" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-collapse-item>

                <!-- 主体 -->
                <el-collapse-item title="主体" name="body">
                  <el-form-item label="标题" prop="title">
                    <el-input v-model="form.title" placeholder="请输入公文标题" />
                    <div class="field-actions">
                      <el-button link @click="generateTitleFromContent" :disabled="!form.content">
                        <el-icon>
                          <MagicIcon />
                        </el-icon> 从正文生成标题
                      </el-button>
                    </div>
                  </el-form-item>

                  <el-form-item label="主送机关" prop="recipient">
                    <el-input v-model="form.recipient" placeholder="请输入主送机关名称" />
                  </el-form-item>

                  <el-form-item label="正文内容" prop="content">
                    <el-input v-model="form.content" type="textarea" :rows="12" placeholder="请输入公文正文内容，支持Markdown格式" />
                    <div class="field-actions">
                      <el-button link @click="generateContentFromTopic">
                        <el-icon>
                          <MagicIcon />
                        </el-icon> 从主题生成正文
                      </el-button>
                      <el-button link @click="uploadFile">
                        <el-icon>
                          <Upload />
                        </el-icon> 上传文件作为正文
                      </el-button>
                    </div>
                  </el-form-item>
                </el-collapse-item>

                <!-- 发文机关或签发人署名 -->
                <el-collapse-item title="发文机关或签发人署名" name="signature">
                  <el-form-item label="发文机关署名" prop="senderSignature">
                    <el-input v-model="form.senderSignature" placeholder="请输入发文机关署名" />
                  </el-form-item>

                  <el-form-item label="成文日期" prop="date">
                    <el-date-picker v-model="form.date" type="date" placeholder="选择日期" format="YYYY年MM月DD日"
                      value-format="YYYY年MM月DD日" style="width: 100%" />
                  </el-form-item>

                  <el-form-item label="附注" prop="notes">
                    <el-input v-model="form.notes" placeholder="请输入附注" />
                  </el-form-item>
                </el-collapse-item>

                <!-- 版记 -->
                <el-collapse-item title="版记" name="footer">
                  <el-form-item label="抄送机关" prop="copyTo">
                    <el-input v-model="form.copyTo" type="textarea" :rows="3" placeholder="请输入抄送机关，多个机关请用逗号分隔" />
                  </el-form-item>
                </el-collapse-item>

                <!-- 印发机关和印发日期 -->
                <el-collapse-item title="印发机关和印发日期" name="printing">
                  <el-form-item label="印发机关" prop="printingOrg">
                    <el-input v-model="form.printingOrg" placeholder="请输入印发机关" />
                  </el-form-item>

                  <el-form-item label="印发日期" prop="printingDate">
                    <el-date-picker v-model="form.printingDate" type="date" placeholder="选择印发日期" format="YYYY年MM月DD日"
                      value-format="YYYY年MM月DD日" style="width: 100%" />
                  </el-form-item>
                </el-collapse-item>
              </el-collapse>

              <el-form-item label="输入格式">
                <el-radio-group v-model="form.formatType">
                                  <el-radio :value="'markdown'">Markdown</el-radio>
                <el-radio :value="'plain'">纯文本</el-radio>
                </el-radio-group>
              </el-form-item>

              <!-- 操作按钮 -->
              <el-form-item>
                <el-button type="primary" @click="generateDocument" :loading="generating">
                  <el-icon>
                    <Document />
                  </el-icon>
                  生成公文
                </el-button>
                <el-button @click="resetForm">
                  <el-icon>
                    <Refresh />
                  </el-icon>
                  重置
                </el-button>
                <el-button type="success" @click="previewTemplate" :disabled="!form.templateType">
                  <el-icon>
                    <View />
                  </el-icon>
                  预览模板
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <!-- 右侧：模板预览和最近生成 -->
        <el-col :span="12">
          <!-- 模板预览卡片 -->
          <el-card class="template-preview-card" v-if="form.templateType">
            <template #header>
              <span>{{ getTemplateName(form.templateType) }}</span>
            </template>
            <div class="template-preview-content">
              <!-- 模板图片预览 -->
              <div class="template-image-preview">
                <div v-for="image in templateImages" :key="image.index" class="image-container">
                  <el-image :src="image.url" :alt="`${getTemplateName(form.templateType)} 第${image.index}页`"
                    fit="contain" class="preview-image" loading="lazy">
                    <template #error>
                      <div class="image-error">
                        <el-icon>
                          <Picture />
                        </el-icon>
                        <div>模板图片加载失败</div>
                      </div>
                    </template>
                  </el-image>
                  <div class="image-caption">第 {{ image.index }} 页</div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 最近生成的文档 -->
          <el-card class="recent-card" v-if="recentDocuments.length > 0">
            <template #header>
              <span>最近生成</span>
            </template>
            <div class="recent-list">
              <div v-for="doc in recentDocuments" :key="doc.id" class="recent-item">
                <div class="recent-info">
                  <div class="recent-title">{{ doc.title }}</div>
                  <div class="recent-time">{{ doc.createTime }}</div>
                </div>
                <div class="recent-actions">
                  <el-button link @click="previewDocument(doc.previewUrl)" title="预览">
                    <el-icon>
                      <View />
                    </el-icon>
                  </el-button>
                  <el-button link @click="downloadDocument(doc.downloadUrl)" title="下载">
                    <el-icon>
                      <Download />
                    </el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 文件上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传文件" width="500px">
      <el-upload ref="uploadRef" :action="uploadUrl" :on-success="handleUploadSuccess" :on-error="handleUploadError"
        :before-upload="beforeUpload" drag accept=".md,.docx,.doc,.txt" :headers="uploadHeaders">
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
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { Upload, Document, Refresh, View, Download, UploadFilled, Picture } from '@element-plus/icons-vue'
import MagicIcon from '../components/MagicIcon.vue'
import { getTemplates, generateDocument as generateDocumentApi, uploadFile as uploadFileApi } from '../api/document'

export default {
  name: 'DocumentGenerator',
  components: {
    Upload, Document, Refresh, View, Download, UploadFilled, Picture, MagicIcon
  },
  setup() {
    const router = useRouter()
    const formRef = ref()
    const uploadRef = ref()
    const templates = ref([])
    const generating = ref(false)
    const uploadDialogVisible = ref(false)
    const recentDocuments = ref([])
    const uploadUrl = '/api/upload'
    const uploadHeaders = { 'X-Requested-With': 'XMLHttpRequest' }
    const activeCollapse = ref(['body']) // 默认展开主体部分

    const form = reactive({
      templateType: '',
      // 版头字段
      copyNumber: '',
      securityLevel: '一般',
      securityPeriod: '',
      urgencyLevel: '一般',
      sender: '',
      senderSymbol: '',
      senderCode: '',
      year: new Date().getFullYear().toString(),
      serialNumber: '',
      // 主体字段
      title: '',
      recipient: '',
      content: '',
      // 发文机关或签发人署名
      senderSignature: '',
      date: '',
      notes: '',
      // 版记
      copyTo: '',
      // 印发机关和印发日期
      printingOrg: '',
      printingDate: '',
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
        // 定义正确的15种公文类型
        const correctTemplates = [
          { id: 'baogao', name: '报告', description: '向上级机关汇报工作、反映情况、回复询问' },
          { id: 'gongbao', name: '公报', description: '公开发布重要决议、决定或重大事件' },
          { id: 'gonggao', name: '公告', description: '向国内外宣布重要事项或者法定事项' },
          { id: 'hansong', name: '函送', description: '向有关单位送交公文或资料' },
          { id: 'jiyao', name: '纪要', description: '记载会议主要情况和议定事项' },
          { id: 'jueding', name: '决定', description: '对重要事项或重大行动作出安排' },
          { id: 'jueyi', name: '决议', description: '会议讨论通过的重要事项的决策' },
          { id: 'minglin', name: '命令', description: '依照有关法律公布行政法规和规章、宣布施行重大强制性措施' },
          { id: 'pifu', name: '批复', description: '答复下级机关请示事项' },
          { id: 'qingshi', name: '请示', description: '向上级机关请求指示或批准' },
          { id: 'tongbao', name: '通报', description: '表彰先进、批评错误、传达重要精神或情况' },
          { id: 'tonggao', name: '通告', description: '公开宣布重要事项或者法定事项' },
          { id: 'tongzhi', name: '通知', description: '发布、传达要求下级机关执行和有关单位周知或者执行的事项' },
          { id: 'yian', name: '议案', description: '正式提出审议事项的文书' },
          { id: 'yijian', name: '意见', description: '对重要问题提出见解和处理办法' }
        ]

        try {
          const response = await getTemplates()
          if (response.data && response.data.length > 0) {
            // 过滤API返回的数据，确保只包含正确的15种公文类型
            const filteredTemplates = response.data.filter(template => {
              // 检查是否是正确的公文类型
              return correctTemplates.some(correctTemplate => correctTemplate.id === template.id)
            })

            // 如果过滤后的数据不足15种，则使用本地定义的数据
            if (filteredTemplates.length === 15) {
              templates.value = filteredTemplates
            } else {
              console.log('API返回的数据不完整，使用本地定义的数据')
              templates.value = correctTemplates
            }
          } else {
            // 如果API没有返回数据，使用本地定义的模板数据
            templates.value = correctTemplates
          }
        } catch (error) {
          console.error('API请求失败，使用本地定义的数据')
          templates.value = correctTemplates
        }

        // 检查URL参数中是否有模板类型
        const urlParams = new URLSearchParams(window.location.search)
        const templateParam = urlParams.get('template')
        if (templateParam) {
          form.templateType = templateParam
          console.log('从URL参数中获取模板类型:', templateParam)
          // 加载模板图片
          loadTemplateImages(templateParam)
        }
      } catch (error) {
        console.error('加载模板失败:', error)
        // 使用本地定义的模板数据作为备份
        templates.value = [
          { id: 'baogao', name: '报告', description: '向上级机关汇报工作、反映情况、回复询问' },
          { id: 'gongbao', name: '公报', description: '公开发布重要决议、决定或重大事件' },
          { id: 'gonggao', name: '公告', description: '向国内外宣布重要事项或者法定事项' },
          { id: 'hansong', name: '函送', description: '向有关单位送交公文或资料' },
          { id: 'jiyao', name: '纪要', description: '记载会议主要情况和议定事项' },
          { id: 'jueding', name: '决定', description: '对重要事项或重大行动作出安排' },
          { id: 'jueyi', name: '决议', description: '会议讨论通过的重要事项的决策' },
          { id: 'minglin', name: '命令', description: '依照有关法律公布行政法规和规章、宣布施行重大强制性措施' },
          { id: 'pifu', name: '批复', description: '答复下级机关请示事项' },
          { id: 'qingshi', name: '请示', description: '向上级机关请求指示或批准' },
          { id: 'tongbao', name: '通报', description: '表彰先进、批评错误、传达重要精神或情况' },
          { id: 'tonggao', name: '通告', description: '公开宣布重要事项或者法定事项' },
          { id: 'tongzhi', name: '通知', description: '发布、传达要求下级机关执行和有关单位周知或者执行的事项' },
          { id: 'yian', name: '议案', description: '正式提出审议事项的文书' },
          { id: 'yijian', name: '意见', description: '对重要问题提出见解和处理办法' }
        ]

        // 检查URL参数中是否有模板类型
        const urlParams = new URLSearchParams(window.location.search)
        const templateParam = urlParams.get('template')
        if (templateParam) {
          form.templateType = templateParam
          console.log('从URL参数中获取模板类型:', templateParam)
        }
      }
    }

    const onTemplateChange = (templateId) => {
      // 根据模板类型设置默认值或特殊处理
      console.log('选择模板:', templateId)
      // 加载模板图片
      loadTemplateImages(templateId)
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
            // 版头字段
            copyNumber: form.copyNumber || '000001',
            securityLevel: form.securityLevel || '一般',
            securityPeriod: form.securityPeriod || '1年',
            urgencyLevel: form.urgencyLevel || '一般',
            sender: form.sender,
            senderSymbol: form.senderSymbol || '文件',
            senderCode: form.senderCode || '',
            year: form.year || '',
            serialNumber: form.serialNumber || '',
            // 主体字段
            title: form.title,
            recipient: form.recipient || '',
            // 署名字段
            senderSignature: form.senderSignature || '',
            date: formattedDate,
            notes: form.notes || '',
            // 版记字段
            copyTo: form.copyTo || '',
            // 印发字段
            printingOrg: form.printingOrg || '',
            printingDate: form.printingDate || formattedDate,
            format_type: form.formatType || 'markdown'
          }
        }

        console.log('准备发送请求:', JSON.stringify(requestData))
        
        try {
          // 使用fetch API直接发送请求，以便更好地处理错误
          const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
          })
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
          
          const result = await response.json()
          console.log('收到响应:', result)
          
          if (result.success) {
            ElMessage.success('公文生成成功！')
  
            // 添加到最近生成列表
            recentDocuments.value.unshift({
              id: Date.now(),
              title: form.title,
              createTime: new Date().toLocaleString(),
              downloadUrl: result.download_url,
              previewUrl: result.download_url.replace('/download/', '/preview/')
            })
  
            // 显示预览和下载选项
            ElMessageBox.confirm(
              '公文生成成功！您可以选择预览或直接下载文档。',
              '生成成功',
              {
                confirmButtonText: '预览文档',
                cancelButtonText: '直接下载',
                distinguishCancelAndClose: true,
                type: 'success'
              }
            ).then(() => {
              // 预览文档
              window.open(result.download_url.replace('/download/', '/preview/'), '_blank')
            }).catch((action) => {
              if (action === 'cancel') {
                // 直接下载
                downloadDocument(result.download_url)
              }
            })
          } else {
            ElMessage.error(result.message || '生成失败')
          }
        } catch (apiError) {
          console.error('API请求失败:', apiError)
          ElMessage.error(`API请求失败: ${apiError.message}`)
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

    const previewDocument = (previewUrl) => {
      if (previewUrl) {
        window.open(previewUrl, '_blank')
      } else if (form.templateType) {
        window.open(`/preview/${form.templateType}`, '_blank')
      }
    }

    const previewTemplate = () => {
      if (form.templateType) {
        // 使用Vue Router导航到模板预览页面
        router.push({
          name: 'TemplatePreview',
          params: { templateId: form.templateType }
        })
      }
    }

    const uploadFile = () => {
      uploadDialogVisible.value = true
    }

    const beforeUpload = (file) => {
      console.log('准备上传文件:', file.name, file.type, file.size)
      const validTypes = ['text/markdown', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'text/plain']
      const validExtensions = ['.md', '.docx', '.doc', '.txt']
      
      // 检查文件类型和扩展名
      const isValidType = validTypes.includes(file.type) || 
                          validExtensions.some(ext => file.name.toLowerCase().endsWith(ext))
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
      console.log('文件上传成功，响应:', response)
      if (response && response.success) {
        form.content = response.content
        uploadDialogVisible.value = false
        ElMessage.success('文件上传成功！')
      } else {
        ElMessage.error(response?.message || '文件解析失败')
      }
    }

    const handleUploadError = (error) => {
      console.error('文件上传失败:', error)
      ElMessage.error('文件上传失败，请稍后再试')
    }

    const downloadDocument = (downloadUrl) => {
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = ''
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }

    // 获取模板名称
    const getTemplateName = (templateId) => {
      const template = templates.value.find(t => t.id === templateId)
      return template ? template.name : '未知模板'
    }

    // 获取模板描述
    const getTemplateDescription = (templateId) => {
      const template = templates.value.find(t => t.id === templateId)
      return template ? template.description : '暂无描述'
    }

    // 获取中文名称的映射
    const chineseNameMap = {
      'baogao': '报告',
      'gongbao': '公报',
      'gonggao': '公告',
      'hansong': '函送',
      'jiyao': '纪要',
      'jueding': '决定',
      'jueyi': '决议',
      'minglin': '命令',
      'pifu': '批复',
      'qingshi': '请示',
      'tongbao': '通报',
      'tonggao': '通告',
      'tongzhi': '通知',
      'yian': '议案',
      'yijian': '意见'
    }

    // 模板图片列表
    const templateImages = ref([])

    // 加载模板图片
    const loadTemplateImages = async (templateId) => {
      if (!templateId) return

      const chineseName = chineseNameMap[templateId] || getTemplateName(templateId)
      console.log('加载模板图片，模板中文名称:', chineseName)

      // 清空当前图片列表
      templateImages.value = []

      // 异步检查图片是否存在
      const checkImageExists = (url) => {
        return new Promise((resolve) => {
          const img = new Image()
          img.onload = () => resolve(true)
          img.onerror = () => resolve(false)
          img.src = url
        })
      }

      // 逐个检查图片是否存在
      let hasImages = false
      for (let i = 1; i <= 10; i++) {
        const imageUrl = `/templates/${chineseName}/${i}.png`
        const exists = await checkImageExists(imageUrl)

        if (exists) {
          templateImages.value.push({
            url: imageUrl,
            index: i
          })
          hasImages = true
        } else {
          // 如果图片不存在，停止检查后续图片
          break
        }
      }

      // 如果没有找到任何图片，显示默认图片
      if (!hasImages) {
        console.log('未找到模板图片，使用默认模板图片')
        templateImages.value.push({
          url: '/templates/default.png',
          index: 1,
          isDefault: true
        })
      }
    }

    // 获取模板图片URL列表
    const getTemplateImages = () => {
      return templateImages.value
    }

    // 从内容生成标题
    const generateTitleFromContent = async () => {
      if (!form.content) {
        ElMessage.warning('请先输入正文内容')
        return
      }

      try {
        const loading = ElLoading.service({
          lock: true,
          text: '正在生成标题...',
          background: 'rgba(0, 0, 0, 0.7)'
        })

        const response = await fetch('/api/generate-title', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            content: form.content
          })
        })

        const result = await response.json()
        loading.close()

        if (result.success) {
          form.title = result.title
          ElMessage.success('标题生成成功')
        } else {
          ElMessage.error(result.message || '标题生成失败')
        }
      } catch (error) {
        ElMessage.error('标题生成失败，请稍后再试')
        console.error('生成标题失败:', error)
      }
    }

    // 从主题生成内容
    const generateContentFromTopic = async () => {
      // 弹出对话框，让用户输入主题
      ElMessageBox.prompt('请输入公文主题', '生成内容', {
        confirmButtonText: '生成',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入公文主题或关键内容'
      }).then(async ({ value }) => {
        if (!value) {
          ElMessage.warning('请输入主题')
          return
        }

        try {
          const loading = ElLoading.service({
            lock: true,
            text: '正在生成内容...',
            background: 'rgba(0, 0, 0, 0.7)'
          })

          const response = await fetch('/api/generate-content', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              topic: value,
              document_type: getTemplateName(form.templateType)
            })
          })

          const result = await response.json()
          loading.close()

          if (result.success) {
            form.content = result.content
            ElMessage.success('内容生成成功')
          } else {
            ElMessage.error(result.message || '内容生成失败')
          }
        } catch (error) {
          ElMessage.error('内容生成失败，请稍后再试')
          console.error('生成内容失败:', error)
        }
      }).catch(() => {
        // 用户取消操作
      })
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
      activeCollapse,
      onTemplateChange,
      generateDocument,
      resetForm,
      previewDocument,
      uploadFile,
      beforeUpload,
      handleUploadSuccess,
      handleUploadError,
      downloadDocument,
      getTemplateName,
      getTemplateDescription,
      templateImages,
      generateTitleFromContent,
      generateContentFromTopic,
      previewTemplate
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

.help-card-top {
  margin-bottom: 30px;
  background-color: #f8f9fa;
}

.help-card-top .help-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}

.help-card-top .help-content>div {
  flex: 1;
  min-width: 250px;
  padding: 0 15px;
}

.template-preview-card,
.recent-card {
  margin-bottom: 20px;
}

.template-preview-content {
  padding: 10px 0;
}

.template-image-preview {
  margin: 15px 0;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.template-image-preview .image-container {
  margin-bottom: 20px;
}

.preview-image {
  width: 100%;
  object-fit: contain;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid #eaeaea;
}

.image-caption {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
  text-align: center;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 150px;
  background-color: #f5f7fa;
  color: #909399;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
}

.image-error .el-icon {
  font-size: 28px;
  margin-bottom: 10px;
}

.template-info h4 {
  font-size: 18px;
  color: #2c3e50;
  margin-bottom: 10px;
}

.template-features h5 {
  font-size: 14px;
  color: #2c3e50;
  margin: 15px 0 5px 0;
}

.template-features p {
  color: #7f8c8d;
  font-size: 13px;
  margin-bottom: 10px;
}

.field-actions {
  margin-top: 8px;
  display: flex;
  gap: 10px;
}

.field-actions .el-button {
  padding: 4px 8px;
  font-size: 12px;
}

.template-actions {
  margin-top: 20px;
  text-align: center;
}

.help-content h4 {
  color: #2c3e50;
  margin: 15px 0 10px 0;
  font-size: 14px;
}

.help-content ol,
.help-content ul {
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

.template-actions {
  margin-top: 20px;
  text-align: center;
}

.help-content h4 {
  color: #2c3e50;
  margin: 15px 0 10px 0;
  font-size: 14px;
}

.help-content ol,
.help-content ul {
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

.recent-actions {
  display: flex;
  gap: 8px;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>