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
      // 模拟AI响应
      var mockResponse = {
          analysis: "这是AI的回复示例，已调整图形位置。",
          fileContent: this.mockFileModification(payload.fileContent)
      };

      setTimeout(mxUtils.bind(this, function() {
          this.handleAIResponse(mockResponse);
      }), 1000);
  },

  mockFileModification: function(xmlContent) {
      // 示例：在XML中随机调整位置
      return `
<mxfile host="localhost" modified="2025-02-06T14:47:17.921Z" agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36" etag="EGt87oz8gWeC0uYaHmWL" version="@DRAWIO-VERSION@" type="device">
  <diagram name="Page-1" id="4hl4CsbpAmtpuRiWuia1">
    <mxGraphModel dx="888" dy="541" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="Gy7hV57ABvt2Qzs7Av8d-3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="Gy7hV57ABvt2Qzs7Av8d-1" target="Gy7hV57ABvt2Qzs7Av8d-2">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="Gy7hV57ABvt2Qzs7Av8d-1" value="" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="40" width="120" height="80" as="geometry" />
        </mxCell>
        <mxCell id="Gy7hV57ABvt2Qzs7Av8d-4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="Gy7hV57ABvt2Qzs7Av8d-2" target="Gy7hV57ABvt2Qzs7Av8d-5">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="300" y="240" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="Gy7hV57ABvt2Qzs7Av8d-2" value="" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="240" y="40" width="120" height="80" as="geometry" />
        </mxCell>
        <mxCell id="Gy7hV57ABvt2Qzs7Av8d-5" value="" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="240" y="240" width="120" height="80" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
`
  },

  handleAIResponse: function(response) {
      this.addMessage('assistant', response.analysis);
      
      if (response.fileContent) {
          var currentFile = this.editorUi.getCurrentFile();
          console.log("handleAI",currentFile)
          console.log("this",this)
          console.log("this.editorUi",this.editorUi)

          if (currentFile) {
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

  addMessage: function(role, content) {
      var msgDiv = document.createElement('div');
      msgDiv.className = 'geAIMessage ' + role;
      msgDiv.textContent = content;
      this.messages.appendChild(msgDiv);
      this.messages.scrollTop = this.messages.scrollHeight;
  }
};