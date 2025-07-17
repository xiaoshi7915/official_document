import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import DocumentGenerator from '../views/DocumentGenerator.vue'
import TemplatePreview from '../views/TemplatePreview.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/generator',
    name: 'DocumentGenerator',
    component: DocumentGenerator
  },
  {
    path: '/preview/:templateId',
    name: 'TemplatePreview',
    component: TemplatePreview,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 添加全局导航守卫，处理路由错误
router.onError((error) => {
  console.error('路由错误:', error)
})

// 添加导航后的钩子
router.afterEach((to, from) => {
  console.log(`路由从 ${from.path} 到 ${to.path}`)
})

export default router