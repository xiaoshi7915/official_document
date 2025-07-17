import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// 获取所有模板
export const getTemplates = () => {
  return api.get('/templates')
}

// 生成文档
export const generateDocument = (data) => {
  return api.post('/generate', data)
}

// 上传文件
export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  return api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取模板预览内容
export const getTemplatePreview = (templateId) => {
  return api.get(`/template-preview/${templateId}`)
}

// 下载文档
export const downloadDocument = (filename) => {
  return api.get(`/download/${filename}`, {
    responseType: 'blob'
  })
}

export default api