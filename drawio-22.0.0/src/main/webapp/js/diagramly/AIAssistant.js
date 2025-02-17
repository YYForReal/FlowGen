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
          this.handleDiagramStreamRequest(message, fileContent);
      } else {
          this.handleNormalRequest(message, fileContent);
      }
  },

  handleStreamRequest: function(message, fileContent) {
    // 创建带加载状态的临时消息
    var tempMsg = this.addMessage('assistant', '▌', true);
    var buffer = '';
    
    // 使用Fetch API替代XMLHttpRequest
    fetch('http://localhost:8000/stream-chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: message,
            current_drawio: fileContent,
            // model_name: "deepseek-chat",
            model_name: "glm-zero-preview"
        })
    }).then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        const processChunk = ({ done, value }) => {
            if (done) {
                tempMsg.innerHTML = this.parseResponse(buffer);
                this.messages.scrollTop = this.messages.scrollHeight;
                this.sendBtn.disabled = false;
                return;
            }
            
            const chunkData = decoder.decode(value);
            chunkData.split('\n\n').forEach(event => {
                if (event.startsWith('data: ')) {
                    try {
                        const jsonData = JSON.parse(event.replace('data: ', ''));
                        if (jsonData.content) {
                            buffer += jsonData.content;
                            tempMsg.innerHTML = this.parseResponse(buffer) + '▌';
                        }
                        if (jsonData.error) {
                            buffer += `[ERROR] ${jsonData.error}`;
                        }
                    } catch (e) {
                        console.error('Parse error:', e);
                    }
                }
            });
            
            reader.read().then(processChunk);
        };
        
        reader.read().then(processChunk);
    }).catch(error => {
        this.addMessage('system', '请求失败: ' + error.message);
        this.sendBtn.disabled = false;
    });
    
    // 禁用发送按钮
    this.sendBtn.disabled = true;
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
          console.log("handleAI currentFile",currentFile)
          console.log("this",this)
          console.log("this.editorUi",this.editorUi)

          if (currentFile) {
              try {
                  currentFile.setData(response.fileContent);
                  this.editorUi.editor.graph.refresh();

                  currentFile.open();

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

  parseResponse: function(raw) {
    // 过滤SSE格式错误信息
    return raw.replace(/^data: \[ERROR\].*?\n\n/gm, '')
             .replace(/(\n\n|\\n)/g, '\n')
             .trim();
  },

  handleDiagramStreamRequest: function(message, fileContent) {
    // 创建带加载状态的临时消息
    var tempMsg = this.addMessage('assistant', '▌', true);
    var analysisBuffer = '';
    var diagramBuffer = '';
    
    console.log('Starting stream request...');
    
    fetch('http://localhost:8000/generate-diagram', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        },
        body: JSON.stringify({
            type: "drawio",
            user_prompt: message,
            current_drawio: fileContent,
            model_name: "glm-zero-preview",
            stream: true
        })
    }).then(response => {
        console.log('Stream response received:', response);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        if (!response.body) {
            throw new Error('ReadableStream not yet supported in this browser.');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        const processChunk = ({ done, value }) => {
            if (done) {
                console.log('Stream complete');
                tempMsg.innerHTML = this.parseResponse(analysisBuffer);
                this.messages.scrollTop = this.messages.scrollHeight;
                this.sendBtn.disabled = false;
                return;
            }
            
            const chunkData = decoder.decode(value);
            console.log('Received chunk:', chunkData);
            
            chunkData.split('\n\n').forEach(event => {
                if (event.startsWith('data: ')) {
                    try {
                        const jsonData = JSON.parse(event.replace('data: ', ''));
                        console.log('Parsed JSON data:', jsonData);
                        
                        switch(jsonData.type) {
                            case 'reasoning':
                                // 显示思考过程
                                tempMsg.innerHTML = this.parseResponse(jsonData.content + '▌');
                                break;
                                
                            case 'analysis':
                                // 更新分析说明
                                analysisBuffer = jsonData.content;
                                tempMsg.innerHTML = this.parseResponse(analysisBuffer + '▌');
                                break;
                                
                            case 'diagram':
                                // 更新图表内容
                                if (jsonData.content && jsonData.diagram_info) {
                                    diagramBuffer = jsonData.content;
                                    // 使用正确的方法更新图表
                                    var currentFile = this.editorUi.getCurrentFile();
                                    if (currentFile) {
                                        try {
                                            currentFile.setData(diagramBuffer);
                                            this.editorUi.editor.graph.refresh();
                                            currentFile.open();
                                            // 直接保存更改
                                            currentFile.directSave(diagramBuffer);
                                            console.log('Diagram updated successfully');
                                        } catch (error) {
                                            console.error('Failed to update diagram:', error);
                                        }
                                    }
                                }
                                break;
                                
                            case 'error':
                                // 显示错误信息
                                console.error('Stream error:', jsonData.content);
                                tempMsg.innerHTML = this.parseResponse(`[ERROR] ${jsonData.content}`);
                                break;
                                
                            case 'final':
                                // 处理最终结果
                                if (jsonData.response) {
                                    const finalResponse = jsonData.response;
                                    tempMsg.innerHTML = this.parseResponse(finalResponse.analysis);
                                    if (finalResponse.content) {
                                        var currentFile = this.editorUi.getCurrentFile();
                                        if (currentFile) {
                                            try {
                                                currentFile.setData(finalResponse.content);
                                                this.editorUi.editor.graph.refresh();
                                                currentFile.open();
                                                currentFile.directSave(finalResponse.content);
                                                console.log('Final diagram update successful');
                                            } catch (error) {
                                                console.error('Failed to update final diagram:', error);
                                            }
                                        }
                                    }
                                }
                                break;
                                
                            case 'usage':
                                // 可以选择是否显示使用量信息
                                console.log('Usage info:', jsonData.content);
                                break;
                        }
                        
                    } catch (e) {
                        console.error('Parse error:', e);
                    }
                }
            });
            
            this.messages.scrollTop = this.messages.scrollHeight;
            reader.read().then(processChunk);
        };
        
        reader.read().then(processChunk);
    }).catch(error => {
        console.error('Stream request failed:', error);
        this.addMessage('system', '请求失败: ' + error.message);
        this.sendBtn.disabled = false;
    });
    
    // 禁用发送按钮
    this.sendBtn.disabled = true;
  }
};