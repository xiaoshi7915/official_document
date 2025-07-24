<template>
  <div class="home">
    <!-- 英雄区域 -->
    <div class="hero-section">
      <div class="hero-background"></div>
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            <span class="title-highlight">智能公文生成系统</span>
          </h1>
          <p class="hero-subtitle">
            基于GB/T9704-2012标准，支持15种公文类型
            <br>让公文写作更规范、更高效、更智能
          </p>
          <div class="hero-stats">
            <div class="stat-item">
              <div class="stat-number">15</div>
              <div class="stat-label">公文类型</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">100%</div>
              <div class="stat-label">标准合规</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">AI</div>
              <div class="stat-label">智能生成</div>
            </div>
          </div>
          <div class="hero-actions">
            <el-button type="primary" size="large" @click="startGenerate" class="primary-btn">
              <el-icon>
                <Edit />
              </el-icon>
              开始生成公文
            </el-button>
            <el-button size="large" @click="viewTemplates" class="secondary-btn">
              <el-icon>
                <View />
              </el-icon>
              查看模板库
            </el-button>
          </div>
        </div>
        <div class="hero-visual">
          <div class="document-preview">
            <div class="doc-header">
              <div class="doc-title">示例公文</div>
              <div class="doc-type">报告</div>
            </div>
            <div class="doc-content">
              <div class="doc-line"></div>
              <div class="doc-line short"></div>
              <div class="doc-line"></div>
              <div class="doc-line short"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能特色区域 -->
    <div class="features-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">核心功能</h2>
          <p class="section-subtitle">专业的公文生成解决方案</p>
        </div>
        <div class="features-grid">
          <div class="feature-card" v-for="feature in features" :key="feature.id">
            <div class="feature-icon">
              <el-icon :size="48">
                <component :is="feature.icon" />
              </el-icon>
            </div>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-description">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 公文类型展示 -->
    <div id="templates" class="templates-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">支持的公文类型</h2>
          <p class="section-subtitle">涵盖党政机关常用公文类型</p>
        </div>
        <div class="templates-grid">
          <div v-for="template in templates" :key="template.id" 
               class="template-card" @click="selectTemplate(template)">
            <div class="template-header">
              <div class="template-icon">
                <el-icon :size="32">
                  <Document />
                </el-icon>
              </div>
              <h3 class="template-name">{{ template.name }}</h3>
            </div>
            <div class="template-body">
              <p class="template-description">{{ template.description }}</p>
            </div>
            <div class="template-footer">
              <el-button type="primary" size="small" @click.stop="previewTemplate($event, template)">
                预览模板
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 使用流程 -->
    <div class="workflow-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">使用流程</h2>
          <p class="section-subtitle">简单三步，生成标准公文</p>
        </div>
        <div class="workflow-steps">
          <div class="workflow-step" v-for="(step, index) in workflowSteps" :key="index">
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-content">
              <h3 class="step-title">{{ step.title }}</h3>
              <p class="step-description">{{ step.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-section">
            <h3>关于系统</h3>
            <p>基于GB/T9704-2012标准的智能公文生成系统，为党政机关提供专业的公文写作解决方案。</p>
          </div>
          <div class="footer-section">
            <h3>技术支持</h3>
            <p>采用先进的AI技术，确保生成的公文内容准确、格式规范。</p>
          </div>
          <div class="footer-section">
            <h3>联系我们</h3>
            <p>如有问题或建议，请联系技术支持团队。</p>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2024 智能公文生成系统. 保留所有权利.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Edit, View, Document, Setting, Upload, Download, 
  Check, Star, Clock, User 
} from '@element-plus/icons-vue'
import { getTemplates } from '../api/document'

export default {
  name: 'Home',
  components: {
    Edit, View, Document, Setting, Upload, Download, Check, Star, Clock, User
  },
  setup() {
    const router = useRouter()
    const templates = ref([])

    // 功能特色数据
    const features = ref([
      {
        id: 1,
        icon: 'Document',
        title: '15种公文类型',
        description: '涵盖公告、通知、报告、请示等常用公文类型，满足不同场景需求'
      },
      {
        id: 2,
        icon: 'Setting',
        title: '标准化格式',
        description: '严格按照GB/T9704-2012标准进行排版，确保格式规范统一'
      },
      {
        id: 3,
        icon: 'Upload',
        title: '多格式支持',
        description: '支持PDF、DOCX、TXT、MD等多种输入格式，灵活便捷'
      },
      {
        id: 4,
        icon: 'Download',
        title: '一键导出',
        description: '生成标准Word文档，可直接使用，无需额外编辑'
      },
      {
        id: 5,
        icon: 'Check',
        title: '智能校验',
        description: '自动检查格式规范，确保公文质量符合标准要求'
      },
      {
        id: 6,
        icon: 'Star',
        title: '模板库',
        description: '丰富的模板库，提供各类公文的参考模板'
      }
    ])

    // 使用流程步骤
    const workflowSteps = ref([
      {
        title: '选择公文类型',
        description: '从15种公文类型中选择合适的模板'
      },
      {
        title: '填写基本信息',
        description: '输入公文标题、发文机关等基本信息'
      },
      {
        title: '生成标准公文',
        description: '系统自动生成符合标准的公文文档'
      }
    ])

    const loadTemplates = async () => {
      try {
        // 使用本地定义的模板数据，确保显示所有15种公文类型
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

        console.log('已加载15种公文类型:', templates.value.map(t => t.name).join(', '))
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
      }
    }

    const startGenerate = () => {
      // 跳转到公文生成页面，默认选择"报告"类型
      router.push({
        path: '/generator',
        query: { template: 'baogao' }
      })
    }

    const viewTemplates = () => {
      // 跳转到首页的公文类型部分
      const templatesSection = document.querySelector('.templates-section')
      if (templatesSection) {
        templatesSection.scrollIntoView({ behavior: 'smooth' })
      } else {
        // 如果找不到元素，则使用锚点跳转
        router.push('/#templates')
      }
    }

    const selectTemplate = (template) => {
      console.log('选择模板:', template)
      // 使用Vue Router导航
      router.push({
        name: 'TemplatePreview',
        params: { templateId: template.id }
      })
    }

    const previewTemplate = (event, template) => {
      // 阻止事件冒泡
      event.stopPropagation()
      console.log('预览模板:', template)
      // 使用Vue Router导航
      router.push({
        name: 'TemplatePreview',
        params: { templateId: template.id }
      })
    }

    onMounted(() => {
      loadTemplates()
    })

    return {
      templates,
      features,
      workflowSteps,
      startGenerate,
      viewTemplates,
      selectTemplate,
      previewTemplate
    }
  }
}
</script>

<style scoped>
/* 全局样式 */
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 英雄区域 */
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  opacity: 0.9;
}

.hero-content {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
  padding: 80px 0;
  max-width: 1200px;
  margin: 0 auto;
  padding-left: 20px;
  padding-right: 20px;
}

.hero-text {
  color: white;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 20px;
  line-height: 1.2;
}

.title-highlight {
  background: linear-gradient(45deg, #ffd700, #ffed4e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 40px;
  opacity: 0.9;
  line-height: 1.6;
}

.hero-stats {
  display: flex;
  gap: 40px;
  margin-bottom: 40px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #ffd700;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

.hero-actions {
  display: flex;
  gap: 20px;
}

.primary-btn {
  background: linear-gradient(45deg, #ffd700, #ffed4e);
  border: none;
  color: #333;
  font-weight: 600;
  padding: 15px 30px;
  border-radius: 50px;
  transition: all 0.3s ease;
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(255, 215, 0, 0.3);
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 15px 30px;
  border-radius: 50px;
  transition: all 0.3s ease;
}

.secondary-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

/* 文档预览 */
.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
}

.document-preview {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  transform: rotate(-5deg);
  transition: transform 0.3s ease;
}

.document-preview:hover {
  transform: rotate(0deg) scale(1.05);
}

.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.doc-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
}

.doc-type {
  background: #667eea;
  color: white;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
}

.doc-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.doc-line {
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  width: 100%;
}

.doc-line.short {
  width: 70%;
}

/* 功能特色区域 */
.features-section {
  padding: 100px 0;
  background: white;
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 15px;
}

.section-subtitle {
  font-size: 1.1rem;
  color: #666;
  max-width: 600px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
}

.feature-card {
  background: white;
  padding: 40px 30px;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  margin-bottom: 20px;
  color: #667eea;
}

.feature-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
}

.feature-description {
  color: #666;
  line-height: 1.6;
}

/* 公文类型区域 */
.templates-section {
  padding: 100px 0;
  background: #f8f9fa;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
}

.template-card {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid #f0f0f0;
}

.template-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.12);
}

.template-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.template-icon {
  color: #667eea;
}

.template-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.template-description {
  color: #666;
  line-height: 1.5;
  margin-bottom: 20px;
}

.template-footer {
  display: flex;
  justify-content: flex-end;
}

/* 使用流程区域 */
.workflow-section {
  padding: 100px 0;
  background: white;
}

.workflow-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 40px;
  margin-top: 60px;
}

.workflow-step {
  text-align: center;
  position: relative;
}

.step-number {
  width: 60px;
  height: 60px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 auto 20px;
}

.step-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.step-description {
  color: #666;
  line-height: 1.6;
}

/* 页脚 */
.footer {
  background: #2c3e50;
  color: white;
  padding: 60px 0 20px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  margin-bottom: 40px;
}

.footer-section h3 {
  font-size: 1.2rem;
  margin-bottom: 15px;
  color: #ffd700;
}

.footer-section p {
  color: #bdc3c7;
  line-height: 1.6;
}

.footer-bottom {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #34495e;
  color: #95a5a6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 40px;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-stats {
    justify-content: center;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .templates-grid {
    grid-template-columns: 1fr;
  }

  .workflow-steps {
    grid-template-columns: 1fr;
  }

  .footer-content {
    grid-template-columns: 1fr;
    text-align: center;
  }
}
</style>