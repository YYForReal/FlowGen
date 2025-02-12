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

      // 添加流式控制容器
      this.controls = document.createElement('div');
      this.controls.className = 'geAIControls';
      
      // 流式输出复选框
      this.streamCheckbox = document.createElement('input');
      this.streamCheckbox.type = 'checkbox';
      this.streamCheckbox.id = 'streamCheckbox';
      this.streamCheckbox.checked = false;
      
      // 复选框标签
      var checkboxLabel = document.createElement('label');
      checkboxLabel.htmlFor = 'streamCheckbox';
      checkboxLabel.textContent = '流式输出';
      
      this.controls.appendChild(this.streamCheckbox);
      this.controls.appendChild(checkboxLabel);
      this.controls.appendChild(this.sendBtn);  // 将发送按钮移到控制区
      
      this.inputContainer.appendChild(this.controls);  // 更新容器结构
      
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
      
      // 添加流式输出开关
      var streamOutput = document.getElementById('streamCheckbox').checked;
      
      // 修改为真实请求（带流式处理）
      if(streamOutput) {
          this.handleStreamRequest(message, fileContent);
      } else {
          this.handleNormalRequest(message, fileContent);
      }
  },

  handleStreamRequest: function(message, fileContent) {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', 'http://localhost:8000/generate-diagram');
      xhr.setRequestHeader('Content-Type', 'application/json');
      
      // 创建带加载状态的临时消息
      var tempMsg = this.addMessage('assistant', '▌', true); // 初始光标提示
      var buffer = '';
      var lastUpdate = 0;
      
      xhr.onprogress = function() {
          if (xhr.responseText) {
              buffer += xhr.responseText;
              // 节流更新（每100ms更新一次）
              if (Date.now() - lastUpdate > 100) {
                  tempMsg.innerHTML = this.parseResponse(buffer);
                  this.messages.scrollTop = this.messages.scrollHeight;
                  lastUpdate = Date.now();
              }
          }
      }.bind(this);
      
      xhr.onload = function() {
          // 最终更新确保显示完整内容
          tempMsg.innerHTML = this.parseResponse(buffer);
          this.messages.scrollTop = this.messages.scrollHeight;
      }.bind(this);
      
      // 禁用发送按钮防止重复提交
      this.sendBtn.disabled = true;
      xhr.onloadend = function() {
          this.sendBtn.disabled = false;
      }.bind(this);
      
      xhr.send(JSON.stringify({
          type: 'flowchart',
          user_prompt: message,
          current_drawio: fileContent,
          stream: true,
        //   model_name: "glm-zero-preview"
        //   model_name: "deepseek-r1"
          model_name: "deepseek-chat"
      }));
  },

  handleNormalRequest: function(message, fileContent) {
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
          current_drawio: payload.fileContent,
          model_name: "deepseek-chat"
        //   model_name: "deepseek-r1"
        // model_name: "glm-zero-preview"
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
          console.log("AIRequest data:",data)
          if (data.success) {
              // 处理成功响应
              this.handleAIResponse({
                  analysis: data.analysis,
                  fileContent: data.content
              });
          } else {
              // 处理错误情况
              this.addMessage('system', '抱歉，生成图表时出现错误：' + (data.error || data.analysis || '未知错误'));
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
          console.log("handleAI",currentFile)
          console.log("this",this)
          console.log("this.editorUi",this.editorUi)

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
              // 直接调用保存方法
              currentFile.directSave(response.fileContent);
              if (this.sync != null)
                {
                  console.log("this.sync sendLocalChanges")
                  this.sync.sendLocalChanges();
                }
          }
      }
  },

  addMessage: function(role, content, isTemp) {
      var msgDiv = document.createElement('div');
      msgDiv.className = 'geAIMessage ' + role;
      msgDiv.textContent = content;
      this.messages.appendChild(msgDiv);
      this.messages.scrollTop = this.messages.scrollHeight;
      return msgDiv;
  },

  parseResponse: function(responseText) {
      try {
          // 解析SSE格式数据
          var events = responseText.split('\n\n');
          var content = '';
          
          for (var event of events) {
              var lines = event.split('\n');
              for (var line of lines) {
                  if (line.startsWith('data: ')) {
                      var data = JSON.parse(line.substring(6));
                      content += data.answer_content || '';
                      // 添加打字机光标效果
                      if (data.is_answering) {
                          content += '▌';
                      }
                  }
              }
          }
          return content.replace(/▌$/, ''); // 移除最后一个光标
      } catch (e) {
          console.error('解析响应失败:', e);
          return '响应解析错误';
      }
  }
};