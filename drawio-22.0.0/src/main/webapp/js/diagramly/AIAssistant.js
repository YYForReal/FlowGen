var AIAssistant = function(editorUi) {
  this.editorUi = editorUi;
  this.init();
};

AIAssistant.prototype = {
  init: function() {
      this.createPanel();
      this.bindEvents();
  },

  createPanel: function() {
      this.container = document.createElement('div');
      this.container.className = 'geAIContainer';
      
      this.header = document.createElement('div');
      this.header.className = 'geAIHeader';
      this.header.textContent = 'AI Assistant';
      
      this.messages = document.createElement('div');
      this.messages.className = 'geAIMessages';
      
      this.inputContainer = document.createElement('div');
      this.inputContainer.className = 'geAIInputContainer';
      
      this.input = document.createElement('textarea');
      this.input.className = 'geAIInput';
      this.input.placeholder = 'Type your message...';
      
      this.sendBtn = document.createElement('button');
      this.sendBtn.className = 'geAISendBtn';
      this.sendBtn.textContent = 'Send';
      
      this.inputContainer.appendChild(this.input);
      this.inputContainer.appendChild(this.sendBtn);
      
      this.container.appendChild(this.header);
      this.container.appendChild(this.messages);
      this.container.appendChild(this.inputContainer);
      
      document.body.appendChild(this.container);
  },

  bindEvents: function() {
      mxEvent.addListener(this.sendBtn, 'click', mxUtils.bind(this, this.handleSend));
      mxEvent.addListener(this.input, 'keypress', mxUtils.bind(this, function(evt) {
          if (evt.keyCode === 13 && !evt.shiftKey) {
              this.handleSend();
              evt.preventDefault();
          }
      }));
  },

  handleSend: function() {
      var message = mxUtils.trim(this.input.value);
      if (!message) return;

      this.addMessage('user', message);
      this.input.value = '';

      // 获取当前文件内容
      var currentFile = this.editorUi.getCurrentFile();
      var fileContent = currentFile ? currentFile.getData() : '';
      console.log("handleSend currentFile:",currentFile)

      console.log("handleSend fileContent:",fileContent)
      // Mock请求
      this.mockAIRequest({
          message: message,
          fileContent: fileContent
      });
  },

  mockAIRequest: function(payload) {
      // 显示加载状态
      this.addMessage('system', '正在思考中...');
      
      // 准备请求数据
      var requestData = {
          type: 'flowchart',  // 可以根据实际图表类型动态设置
          user_prompt: payload.message,
          current_drawio: payload.fileContent
      };

      // 发送请求到后端
      fetch('http://localhost:8000/generate-diagram', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData)
      })
      .then(response => response.json())
      .then(data => {
          // 移除加载状态消息
          this.messages.removeChild(this.messages.lastChild);
          
          if (data.success) {
              // 处理成功响应
              this.handleAIResponse({
                  analysis: data.analysis,
                  fileContent: data.content
              });
          } else {
              // 处理错误情况
              this.addMessage('system', '抱歉，生成图表时出现错误：' + (data.error || '未知错误'));
          }
      })
      .catch(error => {
          // 移除加载状态消息
          this.messages.removeChild(this.messages.lastChild);
          // 显示错误消息
          this.addMessage('system', '请求失败：' + error.message);
          console.error('API请求错误:', error);
      });
  },

  handleAIResponse: function(response) {
      // 显示AI的分析回复
      if (response.analysis) {
          this.addMessage('assistant', response.analysis);
      }
      
      // 更新图表内容
      if (response.fileContent) {
          var currentFile = this.editorUi.getCurrentFile();
          if (currentFile) {
              try {
                  currentFile.setData(response.fileContent);
                  this.editorUi.editor.graph.refresh();
                  // 可选：添加成功提示
                  this.addMessage('system', '图表已更新');
              } catch (error) {
                  console.error('更新图表失败:', error);
                  this.addMessage('system', '更新图表时出现错误：' + error.message);
              }
          }
      }
  },

  addMessage: function(role, content) {
      var msgDiv = document.createElement('div');
      msgDiv.className = 'geAIMessage ' + role;
      msgDiv.textContent = content;
      this.messages.appendChild(msgDiv);
      this.messages.scrollTop = this.messages.scrollHeight;
  }
};