<template>
  <div id="app">
    <el-container class="app-container">
      <el-header class="app-header">
        <div class="header-content">
          <h1 class="app-title">
            <el-icon><Document /></el-icon>
            党政机关公文生成智能体
          </h1>
          <div class="header-info">
            <span>基于GB/T9704-2012标准</span>
          </div>
        </div>
      </el-header>
      
      <el-main class="app-main">
        <router-view />
      </el-main>
      
      <el-footer class="app-footer">
        <div class="footer-content">
          <p>&copy; 2025 党政机关公文生成智能体 - 符合GB/T9704-2012标准</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import { Document } from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    Document
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Microsoft YaHei', sans-serif;
  height: 100vh;
}

.app-container {
  height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.app-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  font-weight: 600;
}

.header-info {
  font-size: 14px;
  opacity: 0.9;
}

.app-main {
  background-color: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.app-footer {
  background-color: #2c3e50;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
}

.footer-content {
  text-align: center;
  font-size: 14px;
}
</style>