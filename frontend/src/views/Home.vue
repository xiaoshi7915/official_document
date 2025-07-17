<template>
  <div class="home">
    <div class="hero-section">
      <div class="hero-content">
        <h2 class="hero-title">专业的党政机关公文生成工具</h2>
        <p class="hero-subtitle">
          严格遵循GB/T9704-2012标准，支持15种公文类型，
          <br>让公文写作更规范、更高效
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="startGenerate">
            <el-icon><Edit /></el-icon>
            开始生成公文
          </el-button>
          <el-button size="large" @click="viewTemplates">
            <el-icon><View /></el-icon>
            查看模板
          </el-button>
        </div>
      </div>
    </div>

    <div class="features-section">
      <div class="container">
        <h3 class="section-title">功能特色</h3>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon size="40"><Document /></el-icon>
            </div>
            <h4>15种公文类型</h4>
            <p>涵盖公告、通知、报告、请示等常用公文类型</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon size="40"><Setting /></el-icon>
            </div>
            <h4>标准化格式</h4>
            <p>严格按照GB/T9704-2012标准进行排版</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon size="40"><Upload /></el-icon>
            </div>
            <h4>多格式支持</h4>
            <p>支持Markdown、Word等多种输入格式</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon size="40"><Download /></el-icon>
            </div>
            <h4>一键导出</h4>
            <p>生成标准Word文档，可直接使用</p>
          </div>
        </div>
      </div>
    </div>

    <div class="templates-section">
      <div class="container">
        <h3 class="section-title">支持的公文类型</h3>
        <div class="templates-grid">
          <div 
            v-for="template in templates" 
            :key="template.id"
            class="template-card"
            @click="selectTemplate(template)"
          >
            <div class="template-header">
              <h4>{{ template.name }}</h4>
            </div>
            <div class="template-body">
              <p>{{ template.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Edit, View, Document, Setting, Upload, Download } from '@element-plus/icons-vue'
import { getTemplates } from '../api/document'

export default {
  name: 'Home',
  components: {
    Edit, View, Document, Setting, Upload, Download
  },
  setup() {
    const router = useRouter()
    const templates = ref([])

    const loadTemplates = async () => {
      try {
        const response = await getTemplates()
        templates.value = response.data
      } catch (error) {
        console.error('加载模板失败:', error)
      }
    }

    const startGenerate = () => {
      router.push('/generator')
    }

    const viewTemplates = () => {
      router.push('/generator')
    }

    const selectTemplate = (template) => {
      console.log('选择模板:', template)
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
      startGenerate,
      viewTemplates,
      selectTemplate
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 20px;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 20px;
  margin-bottom: 40px;
  opacity: 0.9;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.features-section, .templates-section {
  padding: 80px 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 36px;
  font-weight: 600;
  margin-bottom: 50px;
  color: #2c3e50;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.feature-card {
  background: white;
  padding: 40px 30px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  color: #667eea;
  margin-bottom: 20px;
}

.feature-card h4 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #2c3e50;
}

.feature-card p {
  color: #7f8c8d;
  line-height: 1.6;
}

.templates-section {
  background-color: #f8f9fa;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.template-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.template-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.template-header h4 {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
}

.template-body p {
  color: #7f8c8d;
  line-height: 1.5;
  font-size: 14px;
}
</style>