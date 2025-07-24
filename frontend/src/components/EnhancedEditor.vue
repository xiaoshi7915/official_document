<template>
  <div class="enhanced-editor">
    <!-- 编辑器工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <!-- AI功能按钮 -->
        <el-button-group class="ai-buttons">
          <el-button 
            type="primary" 
            size="small" 
            @click="handleAIAction('continue')"
            :disabled="!hasSelection"
            title="续写选中内容"
          >
            <el-icon><Edit /></el-icon>
            续写
          </el-button>
          <el-button 
            type="success" 
            size="small" 
            @click="handleAIAction('expand')"
            :disabled="!hasSelection"
            title="扩写选中内容"
          >
            <el-icon><Expand /></el-icon>
            扩写
          </el-button>
          <el-button 
            type="warning" 
            size="small" 
            @click="handleAIAction('summarize')"
            :disabled="!hasSelection"
            title="缩写选中内容"
          >
            <el-icon><DocumentCopy /></el-icon>
            缩写
          </el-button>
          <el-button 
            type="info" 
            size="small" 
            @click="handleAIAction('rewrite')"
            :disabled="!hasSelection"
            title="重写选中内容"
          >
            <el-icon><Refresh /></el-icon>
            重写
          </el-button>
          <el-button 
            type="danger" 
            size="small" 
            @click="handleAIAction('polish')"
            :disabled="!hasSelection"
            title="润色选中内容"
          >
            <el-icon><Brush /></el-icon>
            润色
          </el-button>
        </el-button-group>
      </div>
      
      <div class="toolbar-right">
        <!-- 字数统计 -->
        <div class="word-count">
          <el-icon><Document /></el-icon>
          <span>{{ wordCount }} 字</span>
        </div>
        
        <!-- 查找替换按钮 -->
        <el-button-group class="search-buttons">
          <el-button 
            type="default" 
            size="small" 
            @click="showFindDialog = true"
            title="查找"
          >
            <el-icon><Search /></el-icon>
            查找
          </el-button>
          <el-button 
            type="default" 
            size="small" 
            @click="showReplaceDialog = true"
            title="替换"
          >
            <el-icon><Switch /></el-icon>
            替换
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 编辑器主体 -->
    <div class="editor-container">
      <textarea
        ref="editorRef"
        v-model="content"
        class="markdown-editor"
        :placeholder="placeholder"
        @input="handleInput"
        @select="handleSelect"
        @focus="handleFocus"
        @blur="handleBlur"
      ></textarea>
    </div>

    <!-- 查找对话框 -->
    <el-dialog v-model="showFindDialog" title="查找" width="400px">
      <div class="find-dialog">
        <el-input
          v-model="findText"
          placeholder="请输入要查找的内容"
          @keyup.enter="findNext"
        >
          <template #append>
            <el-button @click="findNext">查找</el-button>
          </template>
        </el-input>
        <div class="find-options">
          <el-checkbox v-model="findCaseSensitive">区分大小写</el-checkbox>
          <el-checkbox v-model="findWholeWord">全字匹配</el-checkbox>
        </div>
      </div>
    </el-dialog>

    <!-- 替换对话框 -->
    <el-dialog v-model="showReplaceDialog" title="查找和替换" width="500px">
      <div class="replace-dialog">
        <el-form>
          <el-form-item label="查找内容">
            <el-input v-model="findText" placeholder="请输入要查找的内容" />
          </el-form-item>
          <el-form-item label="替换为">
            <el-input v-model="replaceText" placeholder="请输入替换内容" />
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="findCaseSensitive">区分大小写</el-checkbox>
            <el-checkbox v-model="findWholeWord">全字匹配</el-checkbox>
          </el-form-item>
        </el-form>
        <div class="replace-actions">
          <el-button @click="findNext">查找下一个</el-button>
          <el-button type="primary" @click="replaceOne">替换</el-button>
          <el-button type="danger" @click="replaceAll">全部替换</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- AI操作对话框 -->
    <el-dialog v-model="showAIDialog" :title="aiDialogTitle" width="600px">
      <div class="ai-dialog">
        <div class="selected-text">
          <h4>选中内容：</h4>
          <div class="text-preview">{{ selectedText }}</div>
        </div>
        <div class="ai-options">
          <el-form>
            <el-form-item label="操作类型">
              <el-select v-model="aiActionType" placeholder="选择操作类型">
                <el-option label="续写" value="continue" />
                <el-option label="扩写" value="expand" />
                <el-option label="缩写" value="summarize" />
                <el-option label="重写" value="rewrite" />
                <el-option label="润色" value="polish" />
              </el-select>
            </el-form-item>
            <el-form-item label="额外要求（可选）">
              <el-input
                v-model="aiExtraRequirements"
                type="textarea"
                :rows="3"
                placeholder="请输入额外的要求或说明"
              />
            </el-form-item>
          </el-form>
        </div>
        <div class="ai-actions">
          <el-button @click="showAIDialog = false">取消</el-button>
          <el-button type="primary" @click="executeAIAction" :loading="aiProcessing">
            执行操作
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { 
  Edit, Expand, DocumentCopy, Refresh, Brush, 
  Document, Search, Switch 
} from '@element-plus/icons-vue'

export default {
  name: 'EnhancedEditor',
  components: {
    Edit, Expand, DocumentCopy, Refresh, Brush, Document, Search, Switch
  },
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: '请输入内容，支持Markdown格式'
    }
  },
  emits: ['update:modelValue', 'ai-action'],
  setup(props, { emit }) {
    const editorRef = ref(null)
    const content = ref(props.modelValue)
    const selectedText = ref('')
    const hasSelection = ref(false)
    const wordCount = ref(0)
    
    // 查找替换相关
    const showFindDialog = ref(false)
    const showReplaceDialog = ref(false)
    const findText = ref('')
    const replaceText = ref('')
    const findCaseSensitive = ref(false)
    const findWholeWord = ref(false)
    
    // AI操作相关
    const showAIDialog = ref(false)
    const aiActionType = ref('')
    const aiExtraRequirements = ref('')
    const aiProcessing = ref(false)
    
    const aiDialogTitle = computed(() => {
      const titles = {
        continue: '续写内容',
        expand: '扩写内容',
        summarize: '缩写内容',
        rewrite: '重写内容',
        polish: '润色内容'
      }
      return titles[aiActionType.value] || 'AI操作'
    })

    // 监听内容变化
    watch(() => props.modelValue, (newVal) => {
      content.value = newVal
      updateWordCount()
    })

    watch(content, (newVal) => {
      emit('update:modelValue', newVal)
      updateWordCount()
    })

    // 更新字数统计
    const updateWordCount = () => {
      const text = content.value || ''
      // 中文字符计数
      const chineseCount = (text.match(/[\u4e00-\u9fa5]/g) || []).length
      // 英文单词计数
      const englishWords = text.match(/[a-zA-Z]+/g) || []
      const englishCount = englishWords.length
      wordCount.value = chineseCount + englishCount
    }

    // 处理输入
    const handleInput = () => {
      updateWordCount()
    }

    // 处理选择
    const handleSelect = () => {
      const textarea = editorRef.value
      if (textarea) {
        const start = textarea.selectionStart
        const end = textarea.selectionEnd
        selectedText.value = content.value.substring(start, end)
        hasSelection.value = selectedText.value.length > 0
      }
    }

    // 处理焦点
    const handleFocus = () => {
      handleSelect()
    }

    // 处理失焦
    const handleBlur = () => {
      // 延迟清除选择状态，避免按钮点击时立即禁用
      setTimeout(() => {
        if (!showAIDialog.value) {
          hasSelection.value = false
        }
      }, 100)
    }

    // 处理AI操作
    const handleAIAction = (action) => {
      if (!selectedText.value) {
        ElMessage.warning('请先选择要操作的内容')
        return
      }
      
      aiActionType.value = action
      showAIDialog.value = true
    }

    // 执行AI操作
    const executeAIAction = async () => {
      if (!selectedText.value) {
        ElMessage.warning('没有选中内容')
        return
      }

      aiProcessing.value = true
      
      try {
        const loading = ElLoading.service({
          lock: true,
          text: '正在处理...',
          background: 'rgba(0, 0, 0, 0.7)'
        })

        // 构建请求数据
        const requestData = {
          action: aiActionType.value,
          selectedText: selectedText.value,
          fullContent: content.value,
          extraRequirements: aiExtraRequirements.value
        }

        // 发送AI操作请求
        const response = await fetch('/api/ai/text-operation', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })

        loading.close()

        if (response.ok) {
          const result = await response.json()
          if (result.success) {
            // 替换选中的文本
            const textarea = editorRef.value
            const start = textarea.selectionStart
            const end = textarea.selectionEnd
            
            const newContent = content.value.substring(0, start) + 
                             result.result + 
                             content.value.substring(end)
            
            content.value = newContent
            
            // 更新光标位置
            await nextTick()
            textarea.focus()
            textarea.setSelectionRange(start, start + result.result.length)
            
            ElMessage.success('操作完成')
            showAIDialog.value = false
          } else {
            ElMessage.error(result.message || '操作失败')
          }
        } else {
          ElMessage.error('网络请求失败')
        }
      } catch (error) {
        console.error('AI操作失败:', error)
        ElMessage.error('操作失败，请稍后再试')
      } finally {
        aiProcessing.value = false
      }
    }

    // 查找功能
    const findNext = () => {
      if (!findText.value) {
        ElMessage.warning('请输入查找内容')
        return
      }

      const textarea = editorRef.value
      const text = content.value
      const searchText = findText.value
      
      let searchRegex
      if (findWholeWord.value) {
        searchRegex = new RegExp(`\\b${searchText}\\b`, findCaseSensitive.value ? 'g' : 'gi')
      } else {
        searchRegex = new RegExp(searchText, findCaseSensitive.value ? 'g' : 'gi')
      }

      const matches = [...text.matchAll(searchRegex)]
      if (matches.length === 0) {
        ElMessage.warning('未找到匹配内容')
        return
      }

      // 找到当前光标位置后的第一个匹配
      const currentPos = textarea.selectionStart
      const nextMatch = matches.find(match => match.index >= currentPos)
      const matchIndex = nextMatch ? nextMatch.index : matches[0].index

      textarea.focus()
      textarea.setSelectionRange(matchIndex, matchIndex + searchText.length)
    }

    // 替换功能
    const replaceOne = () => {
      if (!findText.value || !replaceText.value) {
        ElMessage.warning('请输入查找和替换内容')
        return
      }

      const textarea = editorRef.value
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const selected = content.value.substring(start, end)

      if (selected.toLowerCase() === findText.value.toLowerCase()) {
        const newContent = content.value.substring(0, start) + 
                         replaceText.value + 
                         content.value.substring(end)
        content.value = newContent
        
        // 更新光标位置
        nextTick(() => {
          textarea.focus()
          textarea.setSelectionRange(start, start + replaceText.value.length)
        })
      } else {
        findNext()
      }
    }

    // 全部替换
    const replaceAll = () => {
      if (!findText.value || !replaceText.value) {
        ElMessage.warning('请输入查找和替换内容')
        return
      }

      let searchRegex
      if (findWholeWord.value) {
        searchRegex = new RegExp(`\\b${findText.value}\\b`, findCaseSensitive.value ? 'g' : 'gi')
      } else {
        searchRegex = new RegExp(findText.value, findCaseSensitive.value ? 'g' : 'gi')
      }

      const newContent = content.value.replace(searchRegex, replaceText.value)
      content.value = newContent
      
      ElMessage.success('替换完成')
    }

    // 初始化
    updateWordCount()

    return {
      editorRef,
      content,
      selectedText,
      hasSelection,
      wordCount,
      showFindDialog,
      showReplaceDialog,
      findText,
      replaceText,
      findCaseSensitive,
      findWholeWord,
      showAIDialog,
      aiActionType,
      aiExtraRequirements,
      aiProcessing,
      aiDialogTitle,
      handleInput,
      handleSelect,
      handleFocus,
      handleBlur,
      handleAIAction,
      executeAIAction,
      findNext,
      replaceOne,
      replaceAll
    }
  }
}
</script>

<style scoped>
.enhanced-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  min-height: 48px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-buttons {
  display: flex;
  gap: 4px;
}

.ai-buttons .el-button {
  font-size: 12px;
  padding: 6px 12px;
}

.word-count {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606266;
  font-size: 12px;
}

.search-buttons {
  display: flex;
  gap: 4px;
}

.search-buttons .el-button {
  font-size: 12px;
  padding: 6px 12px;
}

.editor-container {
  position: relative;
}

.markdown-editor {
  width: 100%;
  min-height: 300px;
  padding: 16px;
  border: none;
  outline: none;
  resize: vertical;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  background: #ffffff;
}

.markdown-editor:focus {
  background: #fafafa;
}

.markdown-editor::placeholder {
  color: #c0c4cc;
}

/* 查找替换对话框样式 */
.find-dialog,
.replace-dialog {
  padding: 16px 0;
}

.find-options,
.replace-actions {
  margin-top: 16px;
  display: flex;
  gap: 16px;
  align-items: center;
}

/* AI操作对话框样式 */
.ai-dialog {
  padding: 16px 0;
}

.selected-text {
  margin-bottom: 20px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  border-left: 4px solid #409eff;
}

.selected-text h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.text-preview {
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
  max-height: 100px;
  overflow-y: auto;
  white-space: pre-wrap;
}

.ai-options {
  margin-bottom: 20px;
}

.ai-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .editor-toolbar {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .toolbar-left,
  .toolbar-right {
    justify-content: center;
  }
  
  .ai-buttons {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style> 