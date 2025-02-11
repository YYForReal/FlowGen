# FlowGen Frontend

基于Next.js 14的科研绘图助手前端项目。（TODO）

## 技术栈

- Next.js 14
- React
- TypeScript
- Tailwind CSS
- Shadcn UI

## 开发环境要求

- Node.js >= 18
- npm 或 yarn 或 pnpm

## 项目运行

1. 安装依赖
```bash
npm install
# 或
yarn install
# 或
pnpm install
```

2. 启动开发服务器
```bash
npm run dev
# 或
yarn dev
# 或
pnpm dev
```

3. 打开浏览器访问 http://localhost:3000

## 项目结构

```
frontend/
├── src/
│   ├── app/              # Next.js 应用页面
│   ├── components/       # React组件
│   ├── lib/             # 工具函数和配置
│   └── styles/          # 样式文件
├── public/              # 静态资源
└── package.json         # 项目配置
```

## 主要功能

- 对话式交互界面
- 实时图表预览和编辑
- Draw.io/PlantUML集成
- 响应式布局

## 构建部署

```bash
npm run build
npm run start
```