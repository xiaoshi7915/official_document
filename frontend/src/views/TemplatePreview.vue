<template>
  <div class="template-preview">
    <div class="container">
      <div class="preview-header">
        <el-button @click="goBack" type="primary" plain>
          <el-icon>
            <ArrowLeft />
          </el-icon>
          返回
        </el-button>
        <h2>{{ templateInfo.name }} - 模板预览</h2>
        <div class="header-actions">
          <el-button-group>
            <el-button type="primary" @click="switchPreviewMode('image')" :class="{ active: previewMode === 'image' }">
              <el-icon>
                <Picture />
              </el-icon>
              图片预览
            </el-button>
            <el-button type="primary" @click="switchPreviewMode('html')" :class="{ active: previewMode === 'html' }">
              <el-icon>
                <Document />
              </el-icon>
              HTML预览
            </el-button>
            <el-button type="primary" @click="switchPreviewMode('text')" :class="{ active: previewMode === 'text' }">
              <el-icon>
                <Reading />
              </el-icon>
              文本预览
            </el-button>
          </el-button-group>
          <el-button type="success" @click="useTemplate" style="margin-left: 10px;">
            <el-icon>
              <Edit />
            </el-icon>
            使用此模板
          </el-button>
        </div>
      </div>

      <el-row :gutter="20">
        <el-col :span="16">
          <el-card class="preview-card">
            <template #header>
              <span>模板预览</span>
            </template>
            <div class="document-preview">
              <!-- 图片预览模式 -->
              <div v-if="previewMode === 'image'" class="image-preview">
                <div v-if="imageContent" class="image-container">
                  <img :src="'data:image/png;base64,' + imageContent" alt="模板预览" class="template-image" />
                </div>
                <div v-else class="no-content">
                  <el-empty description="图片预览内容不可用">
                    <template #description>
                      <p>图片预览内容不可用</p>
                      <p class="error-message" v-if="imageError">{{ imageError }}</p>
                    </template>
                  </el-empty>
                </div>
              </div>

              <!-- HTML预览模式 -->
              <div v-else-if="previewMode === 'html'" class="html-preview">
                <div v-if="htmlContent" v-html="htmlContent"></div>
                <div v-else class="no-content">
                  <el-empty description="HTML预览内容不可用"></el-empty>
                </div>
              </div>

              <!-- 文本预览模式 -->
              <div v-else class="text-preview">
                <div class="doc-header">
                  <div class="doc-sender">{{ templateInfo.name === '公告' ? '××市人民政府' : '××机关' }}</div>
                  <div class="doc-line">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</div>
                  <div class="doc-title">{{ getPreviewTitle() }}</div>
                  <div class="doc-number" v-if="showDocNumber">{{ getPreviewDocNumber() }}</div>
                </div>

                <div class="doc-content">
                  <div class="doc-body">
                    <p v-for="(paragraph, index) in getPreviewContent()" :key="index" class="doc-paragraph">
                      {{ paragraph }}
                    </p>
                  </div>
                </div>

                <div class="doc-footer">
                  <div class="doc-signature">
                    <div class="signature-org">{{ templateInfo.name === '公告' ? '××市人民政府' : '××机关' }}
                    </div>
                    <div class="signature-date">{{ getCurrentDate() }}</div>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="info-card">
            <template #header>
              <span>模板信息</span>
            </template>
            <div class="template-info">
              <div class="info-item">
                <label>公文类型：</label>
                <span>{{ templateInfo.name }}</span>
              </div>
              <div class="info-item">
                <label>适用场景：</label>
                <span>{{ templateInfo.description }}</span>
              </div>
              <div class="info-item">
                <label>格式标准：</label>
                <span>GB/T9704-2012</span>
              </div>
              <div class="info-item">
                <label>必填字段：</label>
                <div class="required-fields">
                  <el-tag v-for="field in requiredFields" :key="field" size="small" type="info">
                    {{ field }}
                  </el-tag>
                </div>
              </div>
            </div>
          </el-card>

          <el-card class="usage-card">
            <template #header>
              <span>使用说明</span>
            </template>
            <div class="usage-content">
              <h4>{{ templateInfo.name }}的特点：</h4>
              <ul>
                <li v-for="feature in getTemplateFeatures()" :key="feature">{{ feature }}</li>
              </ul>

              <h4>注意事项：</h4>
              <ul>
                <li v-for="note in getTemplateNotes()" :key="note">{{ note }}</li>
              </ul>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Edit, Document, Reading, Picture } from '@element-plus/icons-vue'
import { ElMessage, ElLoading } from 'element-plus'
import { getTemplates, getTemplatePreview } from '../api/document'

export default {
  name: 'TemplatePreview',
  components: {
    ArrowLeft, Edit, Document, Reading, Picture
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const templateId = route.params.templateId

    // 预览模式：text（文本预览）或 html（HTML预览）
    const previewMode = ref('text')

    const templateInfo = ref({
      id: '',
      name: '',
      description: '',
      category: ''
    })

    const templateData = {
      gonggao: {
        name: '公告',
        description: '向国内外宣布重要事项或者法定事项',
        features: ['面向社会公众', '具有权威性', '内容重要', '格式庄重'],
        notes: ['标题要简洁明确', '内容要准确无误', '发布机关要明确', '日期要准确']
      },
      tongzhi: {
        name: '通知',
        description: '发布、传达要求下级机关执行和有关单位周知或者执行的事项',
        features: ['具有指导性', '要求明确', '时效性强', '适用面广'],
        notes: ['执行要求要明确', '时间节点要清楚', '责任主体要明确', '联系方式要准确']
      },
      baogao: {
        name: '报告',
        description: '向上级机关汇报工作、反映情况、回复询问',
        features: ['汇报性质', '客观真实', '条理清晰', '数据准确'],
        notes: ['情况要客观', '数据要准确', '问题要明确', '建议要可行']
      },
      qingshi: {
        name: '请示',
        description: '向上级机关请求指示或批准',
        features: ['请求性质', '事前行文', '一事一请', '理由充分'],
        notes: ['请示事项要明确', '理由要充分', '方案要可行', '急需上级批准']
      },
      pifu: {
        name: '批复',
        description: '答复下级机关请示事项',
        features: ['答复性质', '针对性强', '态度明确', '指导具体'],
        notes: ['针对请示内容', '态度要明确', '指导要具体', '时效要及时']
      }
    }

    const requiredFields = computed(() => {
      const baseFields = ['标题', '发文机关', '正文内容']
      if (templateId === 'qingshi') {
        return [...baseFields, '收文机关']
      }
      return baseFields
    })

    const showDocNumber = computed(() => {
      return !['jiyao'].includes(templateId)
    })

    const goBack = () => {
      console.log('点击返回按钮')
      // 使用更可靠的导航方式
      router.push('/')
    }

    const useTemplate = () => {
      console.log('使用此模板:', templateId)
      // 使用更可靠的导航方式
      router.push({
        path: '/generator',
        query: { template: templateId }
      })
    }

    const getPreviewTitle = () => {
      const titles = {
        gonggao: '关于××事项的公告',
        tongzhi: '关于××工作的通知',
        baogao: '关于××情况的报告',
        qingshi: '关于××事项的请示',
        pifu: '关于××请示的批复',
        jueding: '关于××事项的决定',
        yijian: '关于××工作的意见',
        tongbao: '关于××情况的通报',
        yihan: '关于××事项的函',
        jiyao: '××会议纪要'
      }
      return titles[templateId] || '公文标题'
    }

    const getPreviewDocNumber = () => {
      const prefixes = {
        gonggao: '××政告',
        tongzhi: '××政发',
        baogao: '××政报',
        qingshi: '××政请',
        pifu: '××政复'
      }
      const prefix = prefixes[templateId] || '××政发'
      return `${prefix}〔2025〕1号`
    }

    // 实际模板内容
    const templateContent = ref({
      content: '',
      paragraphs: []
    })

    // 加载实际模板内容
    const loadTemplateContent = async () => {
      try {
        const loading = ElLoading.service({
          lock: true,
          text: '加载模板内容...',
          background: 'rgba(255, 255, 255, 0.7)'
        })

        console.log('从API加载模板内容:', templateId)
        const response = await getTemplatePreview(templateId)
        loading.close()

        if (response.data.success) {
          console.log('模板内容加载成功:', response.data)
          templateContent.value = {
            content: response.data.content,
            paragraphs: response.data.paragraphs || []
          }
          return true
        } else {
          console.error('模板内容加载失败:', response.data.message)
          ElMessage.warning('模板内容加载失败，显示示例内容')
          return false
        }
      } catch (error) {
        console.error('加载模板内容出错:', error)
        ElMessage.warning('模板内容加载失败，显示示例内容')
        return false
      }
    }

    const getPreviewContent = () => {
      // 如果已经加载了实际模板内容，则使用实际内容
      if (templateContent.value.content) {
        // 将模板内容按段落分割
        return templateContent.value.content.split('\n').filter(line => line.trim());
      }

      // 否则使用示例内容
      const contents = {
        gonggao: [
          '根据××法律法规，现就××事项公告如下：',
          '一、××具体事项内容说明...',
          '二、××相关要求和规定...',
          '三、本公告自发布之日起施行。',
          '特此公告。'
        ],
        tongzhi: [
          '为了××目的，现就××工作通知如下：',
          '一、××工作要求',
          '（一）××具体要求...',
          '（二）××注意事项...',
          '二、××时间安排',
          '请各单位认真贯彻执行。'
        ],
        baogao: [
          '根据××要求，现将××情况报告如下：',
          '一、基本情况',
          '××工作开展情况...',
          '二、主要成效',
          '××取得的成绩...',
          '三、存在问题',
          '××发现的问题...',
          '四、下步工作建议',
          '××改进措施...'
        ]
      }
      return contents[templateId] || ['正文内容示例...', '具体内容根据实际情况填写。']
    }

    const getTemplateFeatures = () => {
      return templateData[templateId]?.features || ['格式规范', '内容完整', '符合标准']
    }

    const getTemplateNotes = () => {
      return templateData[templateId]?.notes || ['内容要准确', '格式要规范', '时间要及时']
    }

    const getCurrentDate = () => {
      const now = new Date()
      return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
    }

    const loadTemplateFromApi = async () => {
      try {
        console.log('从API加载模板数据')
        const response = await getTemplates()
        const templates = response.data
        const apiTemplate = templates.find(t => t.id === templateId)

        if (apiTemplate) {
          console.log('从API找到模板:', apiTemplate)
          // 合并API数据和本地数据
          templateInfo.value = {
            ...apiTemplate,
            features: templateData[templateId]?.features || ['格式规范', '内容完整', '符合标准'],
            notes: templateData[templateId]?.notes || ['内容要准确', '格式要规范', '时间要及时']
          }
          return true
        }
        return false
      } catch (error) {
        console.error('加载模板数据失败:', error)
        return false
      }
    }

    // 切换预览模式
    const switchPreviewMode = (mode) => {
      console.log('切换预览模式:', mode)
      previewMode.value = mode
    }

    // HTML内容
    const htmlContent = ref('')

    // 加载HTML内容
    const loadHtmlContent = async () => {
      try {
        console.log('加载HTML内容')
        const response = await getTemplatePreview(templateId)

        if (response.data.success && response.data.html_content) {
          console.log('HTML内容加载成功')
          htmlContent.value = response.data.html_content
          return true
        } else {
          console.error('HTML内容加载失败:', response.data.html_error || '未知错误')
          return false
        }
      } catch (error) {
        console.error('加载HTML内容出错:', error)
        return false
      }
    }

    onMounted(async () => {
      console.log('模板预览组件加载，模板ID:', templateId)

      // 首先尝试从本地数据加载模板信息
      if (templateData[templateId]) {
        templateInfo.value = {
          id: templateId,
          ...templateData[templateId]
        }
        console.log('已从本地加载模板数据:', templateInfo.value)
      } else {
        // 如果本地没有，尝试从API加载模板信息
        console.log('本地未找到模板数据，尝试从API加载')
        const loaded = await loadTemplateFromApi()

        if (!loaded) {
          console.error('未找到模板数据:', templateId)
          ElMessage.error('未找到模板数据，将返回首页')
          setTimeout(() => {
            router.push('/')
          }, 1500)
          return
        }
      }

      // 加载实际的模板文件内容、HTML内容和图片内容
      await loadTemplateContent()
      await loadHtmlContent()
      await loadImageContent()
    })

    // 修改loadTemplateContent函数，同时加载HTML内容
    const enhancedLoadTemplateContent = async () => {
      const result = await loadTemplateContent()
      await loadHtmlContent()
      return result
    }

    // 图片内容
    const imageContent = ref('')
    const imageError = ref('')
    
    // 加载图片内容
    const loadImageContent = async () => {
      try {
        console.log('加载图片内容')
        const response = await getTemplatePreview(templateId)
        
        if (response.data.success && response.data.image_content) {
          console.log('图片内容加载成功')
          imageContent.value = response.data.image_content
          return true
        } else {
          console.error('图片内容加载失败:', response.data.image_error || '未知错误')
          imageError.value = response.data.image_error || '图片内容加载失败'
          return false
        }
      } catch (error) {
        console.error('加载图片内容出错:', error)
        imageError.value = error.message || '加载图片内容出错'
        return false
      }
    }
    
    // 注意：这里不需要重复的onMounted钩子，已经在上面的onMounted中加载了内容
    
    return {
      templateInfo,
      requiredFields,
      showDocNumber,
      previewMode,
      htmlContent,
      imageContent,
      imageError,
      goBack,
      useTemplate,
      switchPreviewMode,
      getPreviewTitle,
      getPreviewDocNumber,
      getPreviewContent,
      getTemplateFeatures,
      getTemplateNotes,
      getCurrentDate
    }
  }
}
</script>

<style scoped>
.template-preview {
  padding: 20px;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.preview-header h2 {
  color: #2c3e50;
  margin: 0;
}

.preview-card {
  margin-bottom: 20px;
}

.document-preview {
  background: white;
  padding: 40px;
  border: 1px solid #e0e0e0;
  font-family: '仿宋', serif;
  line-height: 1.8;
  min-height: 600px;
}

.doc-header {
  text-align: center;
  margin-bottom: 40px;
}

.doc-sender {
  font-size: 22px;
  font-weight: bold;
  color: #d32f2f;
  margin-bottom: 10px;
}

.doc-line {
  font-size: 14px;
  color: #d32f2f;
  margin-bottom: 20px;
}

.doc-title {
  font-size: 22px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 15px;
}

.doc-number {
  font-size: 16px;
  color: #666;
}

.doc-content {
  margin-bottom: 40px;
}

.doc-paragraph {
  font-size: 16px;
  color: #2c3e50;
  margin-bottom: 15px;
  text-indent: 2em;
  text-align: justify;
}

.doc-footer {
  margin-top: 60px;
}

.doc-signature {
  text-align: right;
}

.signature-org {
  font-size: 16px;
  color: #2c3e50;
  margin-bottom: 20px;
}

.signature-date {
  font-size: 16px;
  color: #2c3e50;
}

/* HTML预览样式 */
.html-preview {
  width: 100%;
  height: 100%;
  min-height: 600px;
  overflow: auto;
}

.html-preview :deep(.document) {
  font-family: SimSun, "宋体", "仿宋", FangSong, serif !important;
}

.html-preview :deep(h1),
.html-preview :deep(h2),
.html-preview :deep(h3) {
  text-align: center;
  color: #d32f2f;
  font-weight: bold;
}

.html-preview :deep(p) {
  margin-bottom: 1em;
  text-indent: 2em;
  line-height: 1.8;
}

.html-preview :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}

.html-preview :deep(td),
.html-preview :deep(th) {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}

/* 图片预览样式 */
.image-preview {
  width: 100%;
  height: 100%;
  min-height: 600px;
  overflow: auto;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.image-container {
  max-width: 100%;
  text-align: center;
}

.template-image {
  max-width: 100%;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.no-content {
  width: 100%;
  height: 100%;
  min-height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

.error-message {
  color: #F56C6C;
  font-size: 12px;
  margin-top: 10px;
  max-width: 80%;
  text-align: center;
}

/* 按钮样式 */
.active {
  font-weight: bold;
  background-color: #409EFF !important;
  color: white !important;
}

.info-card,
.usage-card {
  margin-bottom: 20px;
}

.template-info {
  font-size: 14px;
}

.info-item {
  margin-bottom: 15px;
  display: flex;
  align-items: flex-start;
}

.info-item label {
  font-weight: 600;
  color: #2c3e50;
  min-width: 80px;
  margin-right: 10px;
}

.info-item span {
  color: #7f8c8d;
  flex: 1;
}

.required-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.usage-content h4 {
  color: #2c3e50;
  margin: 15px 0 10px 0;
  font-size: 14px;
}

.usage-content ul {
  margin: 0 0 15px 20px;
  font-size: 13px;
  color: #7f8c8d;
}

.usage-content li {
  margin-bottom: 5px;
  line-height: 1.4;
}
</style>