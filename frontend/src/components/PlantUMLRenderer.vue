<template>
  <div class="plantuml-container">
    <div class="input-area">
      <textarea v-model="umlCode" placeholder="请输入 PlantUML 代码"></textarea>
    </div>
    <div class="preview-area">
      <div id="uml-output"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const umlCode = ref(`@startuml
class A {
  +void method()
}
class B {
  +void method()
}
A --|> B
@enduml`)

// 渲染 UML 图
const renderUML = () => {
  const element = document.getElementById('uml-output')
  if (element && window.plantumluml) {
    window.plantumluml.render('uml-output', umlCode.value)
  }
}

// 监听代码变化
watch(umlCode, () => {
  renderUML()
})

onMounted(() => {
  // 加载 PlantUML 脚本
  const script = document.createElement('script')
  script.src = 'https://cdn.jsdelivr.net/npm/plantuml-uml/dist/plantuml-uml.min.js'
  script.onload = () => {
    renderUML()
  }
  document.head.appendChild(script)
})
</script>

<style scoped>
.plantuml-container {
  display: flex;
  gap: 20px;
  padding: 20px;
}

.input-area {
  flex: 1;
}

.preview-area {
  flex: 1;
}

textarea {
  width: 100%;
  height: 300px;
  padding: 10px;
  font-family: monospace;
}

#uml-output {
  border: 1px solid #ddd;
  padding: 10px;
  min-height: 300px;
}
</style> 