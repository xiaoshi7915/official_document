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
          <el-button type="success" @click="useTemplate">
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
              <div class="template-images">
                <div v-if="templateImages.length > 0" class="image-gallery">
                  <div v-for="(image, index) in templateImages" :key="index" class="image-container">
                    <el-image :src="image.url" :alt="'模板预览 ' + (index + 1)" class="template-image" fit="contain"
                      :preview-src-list="templateImages.map(img => img.url)" :initial-index="index" loading="lazy">
                      <template #error>
                        <div class="image-error">
                          <el-icon>
                            <Picture />
                          </el-icon>
                          <div>图片 {{ index + 1 }} 加载失败</div>
                        </div>
                      </template>
                    </el-image>
                    <div class="image-caption">第 {{ index + 1 }} 页</div>
                  </div>
                </div>
                <div v-else class="no-content">
                  <el-empty description="模板预览内容不可用">
                    <template #description>
                      <p>模板预览内容不可用</p>
                      <p class="error-message">请确保模板图片已上传到正确的目录</p>
                      <p class="error-path">路径: /templates/{{ getChineseName() }}/</p>
                    </template>
                  </el-empty>
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

    // 不再需要预览模式，只使用图片预览

    const templateInfo = ref({
      id: '',
      name: '',
      description: '',
      category: ''
    })

    const templateData = {
      baogao: {
        name: '报告',
        description: '向上级机关汇报工作、反映情况、回复询问',
        features: ['汇报性质', '客观真实', '条理清晰', '数据准确'],
        notes: ['情况要客观', '数据要准确', '问题要明确', '建议要可行']
      },
      gongbao: {
        name: '公报',
        description: '公开发布重要决议、决定或重大事件',
        features: ['权威性强', '内容重大', '公开性强', '格式规范'],
        notes: ['内容要准确', '表述要严谨', '格式要规范', '发布要及时']
      },
      gonggao: {
        name: '公告',
        description: '向国内外宣布重要事项或者法定事项',
        features: ['面向社会公众', '具有权威性', '内容重要', '格式庄重'],
        notes: ['标题要简洁明确', '内容要准确无误', '发布机关要明确', '日期要准确']
      },
      hansong: {
        name: '函送',
        description: '向有关单位送交公文或资料',
        features: ['送交性质', '简明扼要', '明确对象', '附件明确'],
        notes: ['送交内容要明确', '接收单位要准确', '附件要完整', '时间要及时']
      },
      jiyao: {
        name: '纪要',
        description: '记载会议主要情况和议定事项',
        features: ['记录性质', '内容详实', '决议明确', '任务清晰'],
        notes: ['会议内容要完整', '议定事项要明确', '责任分工要清晰', '时间节点要明确']
      },
      jueding: {
        name: '决定',
        description: '对重要事项或重大行动作出安排',
        features: ['决策性质', '权威性强', '内容重大', '执行明确'],
        notes: ['决定事项要明确', '依据要充分', '执行要求要明确', '时间节点要清楚']
      },
      jueyi: {
        name: '决议',
        description: '会议讨论通过的重要事项的决策',
        features: ['集体决策', '权威性强', '内容重大', '表决通过'],
        notes: ['决议内容要明确', '表决程序要规范', '执行要求要明确', '时间节点要清楚']
      },
      minglin: {
        name: '命令',
        description: '依照有关法律公布行政法规和规章、宣布施行重大强制性措施',
        features: ['强制性强', '权威性高', '执行明确', '时效性强'],
        notes: ['命令内容要明确', '依据要充分', '执行要求要严格', '时间节点要明确']
      },
      pifu: {
        name: '批复',
        description: '答复下级机关请示事项',
        features: ['答复性质', '针对性强', '态度明确', '指导具体'],
        notes: ['针对请示内容', '态度要明确', '指导要具体', '时效要及时']
      },
      qingshi: {
        name: '请示',
        description: '向上级机关请求指示或批准',
        features: ['请求性质', '事前行文', '一事一请', '理由充分'],
        notes: ['请示事项要明确', '理由要充分', '方案要可行', '急需上级批准']
      },
      tongbao: {
        name: '通报',
        description: '表彰先进、批评错误、传达重要精神或情况',
        features: ['传达性质', '表彰或批评', '典型案例', '教育意义'],
        notes: ['内容要真实', '典型要突出', '表述要得当', '教育意义要明确']
      },
      tonggao: {
        name: '通告',
        description: '公开宣布重要事项或者法定事项',
        features: ['公开性强', '内容重要', '面向特定区域', '强制性较强'],
        notes: ['内容要明确', '范围要清晰', '时间要准确', '要求要具体']
      },
      tongzhi: {
        name: '通知',
        description: '发布、传达要求下级机关执行和有关单位周知或者执行的事项',
        features: ['具有指导性', '要求明确', '时效性强', '适用面广'],
        notes: ['执行要求要明确', '时间节点要清楚', '责任主体要明确', '联系方式要准确']
      },
      yian: {
        name: '议案',
        description: '正式提出审议事项的文书',
        features: ['提案性质', '内容重要', '程序规范', '审议明确'],
        notes: ['提案内容要明确', '理由要充分', '方案要可行', '程序要规范']
      },
      yijian: {
        name: '意见',
        description: '对重要问题提出见解和处理办法',
        features: ['指导性强', '内容全面', '建议具体', '可操作性强'],
        notes: ['问题分析要准确', '意见要有针对性', '建议要可行', '表述要准确']
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

    // 不再需要加载模板内容的函数，只使用图片预览

    const getPreviewContent = () => {
      // 使用示例内容
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

    // 不再需要切换预览模式和加载HTML内容的函数

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

      // 加载模板图片
      await loadTemplateImages()
    })

    // 修改loadTemplateContent函数，同时加载HTML内容
    const enhancedLoadTemplateContent = async () => {
      const result = await loadTemplateContent()
      await loadHtmlContent()
      return result
    }

    // 模板图片列表
    const templateImages = ref([])

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

    // 获取中文名称
    const getChineseName = () => {
      return chineseNameMap[templateId] || templateInfo.value.name || '未知模板'
    }

    // 加载模板图片
    const loadTemplateImages = async () => {
      try {
        console.log('加载模板图片')

        // 获取中文文件夹名称
        const chineseName = getChineseName()
        console.log('模板中文名称:', chineseName)

        // 构建图片URL列表
        const imageList = []

        // 尝试加载图片并检查是否存在
        const checkImageExists = async (url) => {
          return new Promise((resolve) => {
            const img = new Image()
            img.onload = () => resolve(true)
            img.onerror = () => resolve(false)
            img.src = url
          })
        }

        // 异步检查图片是否存在并添加到列表
        const loadImages = async () => {
          for (let i = 1; i <= 10; i++) {
            const imageUrl = `/templates/${chineseName}/${i}.png`
            const exists = await checkImageExists(imageUrl)
            if (exists) {
              imageList.push({
                url: imageUrl,
                index: i
              })
            } else {
              console.log(`图片 ${i} 不存在，停止加载更多图片`)
              break
            }
          }

          // 更新模板图片列表
          templateImages.value = imageList
          console.log('实际加载的模板图片数量:', imageList.length)
        }

        // 执行图片加载
        await loadImages()

        return true
      } catch (error) {
        console.error('加载模板图片出错:', error)
        return false
      }
    }

    // 注意：这里不需要重复的onMounted钩子，已经在上面的onMounted中加载了内容

    return {
      templateInfo,
      requiredFields,
      showDocNumber,
      templateImages,
      goBack,
      useTemplate,
      getChineseName,
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
  padding: 20px;
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

.image-gallery {
  display: flex;
  flex-direction: column;
  gap: 40px;
  width: 100%;
}

.image-container {
  max-width: 100%;
  text-align: center;
  margin-bottom: 10px;
  position: relative;
}

.template-image {
  max-width: 100%;
  max-height: 800px;
  /* 增加最大高度 */
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
  height: 200px;
  background-color: #f5f7fa;
  color: #909399;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
}

.image-error .el-icon {
  font-size: 28px;
  margin-bottom: 10px;
}

.error-path {
  font-family: monospace;
  background-color: #f5f5f5;
  padding: 3px 6px;
  border-radius: 3px;
  margin-top: 5px;
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