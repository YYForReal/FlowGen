本项目使用 Draw.io 的开源项目。即集成 Draw.io 的 **嵌入式编辑器** 到我们的 Web 应用中。


### 1. **下载并构建 Draw.io 源代码**

首先，你需要下载并构建 Draw.io 的源代码。你可以从 GitHub 上获取 Draw.io 的代码。

#### 步骤：
1. **克隆仓库**：
   打开终端，执行以下命令来克隆 Draw.io 的源代码：
   ```bash
   git clone https://github.com/jgraph/drawio.git
   cd drawio
   ```

    可能会因为仓库太大报错，所以我们需要分段克隆
    ```bash
    # 先克隆一部分
    git clone --depth 1 git@github.com:jgraph/drawio.git
    cd drawio
    ```

    ```bash
    # 然后逐步获取更多历史
    git fetch --deepen 50
    ```

2. **安装依赖**：
   进入 `drawio` 目录后，执行以下命令安装项目的所有依赖：
   ```bash
   npm install
   ```

3. **构建项目**：
   完成依赖安装后，你需要构建前端项目。执行以下命令：
   ```bash
   npm run build
   ```

4. **运行项目**：
   运行以下命令启动本地服务器，启动 Draw.io 编辑器的 Web 版本：
   ```bash
   npm start
   ```

   访问 `http://localhost:8080` 可以查看你的本地 Draw.io 编辑器。

### 2. **将 Draw.io 嵌入到你的应用中**

一旦你完成了 Draw.io 编辑器的构建，你可以将其嵌入到自己的 Web 应用中。最常见的方法是通过 `iframe` 进行嵌入。

#### 步骤：
1. **上传文件到服务器**：
   你需要将你的 Draw.io 编辑器文件托管在一个可以通过 URL 访问的地方。如果你刚刚构建了代码，通常你会在构建目录中找到构建好的静态文件。

2. **嵌入到网页中**：
   在你的网页中，使用 `<iframe>` 标签将 Draw.io 编辑器嵌入。你可以指定编辑器的 URL 和需要加载的 Draw.io 文件的路径。例如：
   ```html
   <iframe width="100%" height="600px" 
       src="https://embed.diagrams.net/?embed=1&ui=atlas&configure=1&spin=1&url=your-drawio-file-url" 
       frameborder="0"></iframe>
   ```
   其中 `your-drawio-file-url` 需要替换为你存储 Draw.io 文件的 URL。如果你希望能够加载和编辑已有的 Draw.io 文件，可以将文件上传到服务器，并提供该文件的路径。

3. **自定义配置**：
   你可以在 URL 上添加一些参数来定制嵌入的编辑器行为：
   - `embed=1`: 启用嵌入模式，移除不必要的 UI 元素。
   - `ui=atlas`: 使用经典的 UI 样式。
   - `configure=1`: 启用配置面板，允许配置一些常见选项。
   - `spin=1`: 显示加载动画。

   例如，嵌入代码示例如下：
   ```html
   <iframe width="100%" height="800px"
       src="https://embed.diagrams.net/?embed=1&ui=atlas&configure=1&spin=1&url=https://example.com/path/to/your-drawio-file.xml"
       frameborder="0"></iframe>
   ```

### 3. **使用 API 与前端交互**

Draw.io 还提供了嵌入编辑器的 JavaScript API，允许你与编辑器进行交互，如加载文件、保存更改、导出图表等。

#### 示例代码：
```html
<!DOCTYPE html>
<html>
  <head>
    <script src="https://www.draw.io/embed.js"></script>
  </head>
  <body>
    <iframe id="drawio-iframe" width="100%" height="800px" frameborder="0"></iframe>
    <script>
      const iframe = document.getElementById('drawio-iframe');
      const src = 'https://embed.diagrams.net/?embed=1&ui=atlas&configure=1&spin=1&url=your-drawio-file-url';
      
      iframe.src = src;

      // 获取 Draw.io 编辑器对象
      iframe.onload = function () {
        const editor = iframe.contentWindow;
        // 这里可以通过 editor 对象调用相关的 API，进行加载、编辑、保存等操作
      };
    </script>
  </body>
</html>
```

### 4. **部署到生产环境**

一旦你完成了前端开发并测试了嵌入功能，你可以将它部署到你的生产环境中。确保将所有的静态文件托管到一个可访问的服务器上，并确保 URL 配置正确。

---

### 总结

通过以上步骤，你可以将 Draw.io 编辑器嵌入到你的前端项目中，允许用户实时渲染和编辑 Draw.io 文件。如果需要进一步的自定义或与后端进行交互，可以参考 [Draw.io 的官方 API 文档](https://www.diagrams.net/doc/faq/embed-diagrams) 进行进一步的开发。
