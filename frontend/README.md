# Z-Image 图像生成前端应用

基于 Next.js 14 和 React 18 开发的 AI 图像生成 Web 应用前端，调用 Z-Image-Turbo Flask 后台服务生成 AI 图像。

## 功能特性

- ✅ **苹果风格设计**：简洁优雅的 UI 设计，遵循苹果设计语言
- ✅ **移动端阻止**：仅支持桌面端访问，移动端显示友好提示
- ✅ **后台服务配置**：可配置后台服务 IP 和端口，支持连接测试
- ✅ **文本生成图片**：支持多张图片批量生成（1-4 张）
- ✅ **参数自定义**：支持图片尺寸、推理步数、随机种子等参数设置
- ✅ **提示词润色**：提供模板库和提示词增强功能
- ✅ **任务状态追踪**：实时轮询任务状态，显示队列位置和进度
- ✅ **图片预览下载**：支持图片预览和下载功能
- ✅ **错误处理**：完善的错误提示和异常处理
- ✅ **响应式设计**：适配不同桌面屏幕尺寸

## 技术栈

### 核心框架

- **Next.js 14+** (App Router)
- **React 18+**
- **TypeScript**

### UI 和样式

- **Tailwind CSS** - 实用优先的 CSS 框架
- **shadcn/ui** - 基于 Radix UI 的组件库
- **Lucide React** - 图标库
- **Framer Motion** - 动画库（可选）

### 工具库

- **axios** - HTTP 客户端
- **react-hot-toast** - 消息提示
- **clsx** - 条件样式处理
- **class-variance-authority** - 组件变体管理

## 快速开始

### 环境要求

- Node.js 18+
- npm 或 yarn 或 pnpm

### 安装步骤

1. **进入前端目录**

```bash
cd frontend
```

2. **安装依赖**

```bash
npm install
# 或
yarn install
# 或
pnpm install
```

3. **配置后台服务地址**

有两种方式配置后台服务地址：

**方式一：使用环境变量（推荐）**

在项目根目录创建 `.env.local` 文件：

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

或者复制 `.env.example` 文件：

```bash
cp .env.example .env.local
```

然后修改 `.env.local` 中的地址。

**方式二：在应用内配置**

- 点击页面右上角的设置图标
- 输入后台服务地址，例如：`http://localhost:5000`
- 点击"测试连接"验证配置
- 点击"保存"保存配置

**优先级**：环境变量 > localStorage 配置 > 默认值 (`http://localhost:5000`)

4. **启动开发服务器**

```bash
npm run dev
# 或
yarn dev
# 或
pnpm dev
```

5. **访问应用**

打开浏览器访问：`http://localhost:3000`

## 功能说明

### 1. 生成图片

1. 在提示词输入框中输入您想要生成的图像描述
2. 设置生成参数：
   - **图片数量**：选择生成 1-4 张图片
   - **图片尺寸**：选择预设尺寸或自定义宽度和高度
   - **推理步数**：1-50，数值越大质量越好但速度越慢（默认 9）
   - **随机种子**：可选，相同种子和提示词会生成相同图像
3. 点击"开始生成"按钮
4. 任务提交后，在右侧任务列表中查看进度

### 2. 提示词润色

1. 点击提示词输入框右侧的"润色"按钮
2. 选择以下方式之一：
   - **使用模板**：从模板库中选择预设提示词模板
   - **增强提示词**：自动为当前提示词添加质量词和风格词

### 3. 预览和下载图片

1. 任务完成后，在任务列表中点击"预览"按钮
2. 在预览模态框中查看完整尺寸图片
3. 点击"下载"按钮保存图片到本地
4. 支持键盘快捷键：按 `ESC` 键关闭预览

### 4. 配置后台服务

1. 点击页面右上角的设置图标（齿轮图标）
2. 输入后台服务的完整 URL 地址
   - 本地：`http://localhost:5000`
   - 远程：`http://192.168.1.100:5000`
3. 点击"测试连接"验证配置是否正确
4. 点击"保存"保存配置

配置会保存到浏览器的 localStorage 中，下次访问会自动加载。

## 项目结构

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # 根布局
│   ├── page.tsx           # 主页面
│   └── globals.css        # 全局样式
├── components/            # React 组件
│   ├── ui/               # shadcn/ui 基础组件
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── textarea.tsx
│   │   ├── dialog.tsx
│   │   ├── select.tsx
│   │   └── label.tsx
│   ├── MobileBlocker.tsx      # 移动端阻止组件
│   ├── SettingsDialog.tsx     # 设置对话框
│   ├── PromptInput.tsx        # 提示词输入组件
│   ├── PromptEnhancer.tsx     # 提示词润色组件
│   ├── ParameterPanel.tsx     # 参数设置面板
│   ├── TaskList.tsx           # 任务列表
│   ├── TaskItem.tsx           # 任务项
│   └── ImagePreview.tsx       # 图片预览模态框
├── hooks/                 # 自定义 Hooks
│   ├── useApiConfig.ts    # API 配置 Hook
│   ├── useTaskPolling.ts # 任务轮询 Hook
│   └── useImageGeneration.ts # 图片生成 Hook
├── lib/                   # 工具函数和配置
│   ├── api.ts            # API 调用封装
│   ├── utils.ts          # 工具函数
│   └── constants.ts      # 常量定义
├── types/                 # TypeScript 类型定义
│   └── index.ts
├── public/               # 静态资源
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── next.config.js
└── README.md
```

## 配置说明

### 后台服务配置

**配置优先级**（从高到低）：
1. 环境变量 `NEXT_PUBLIC_API_BASE_URL`（在 `.env.local` 中配置）
2. localStorage 中保存的配置（通过设置对话框配置）
3. 默认值：`http://localhost:5000`

**方式一：环境变量配置（推荐）**

在项目根目录创建 `.env.local` 文件：

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

或者复制 `.env.example` 文件：

```bash
cp .env.example .env.local
```

**注意**：
- 环境变量必须以 `NEXT_PUBLIC_` 开头才能在客户端访问
- `.env.local` 文件会被 git 忽略，不会提交到代码库
- 修改环境变量后需要重启开发服务器

**方式二：应用内配置**

- 存储位置：浏览器 localStorage
- 存储键名：`api_config`
- 配置方式：通过设置对话框配置

### 默认参数

- **图片尺寸**：1024×1024
- **推理步数**：9
- **图片数量**：1
- **随机种子**：随机

## API 接口

应用调用以下后台 API 接口：

### 1. 健康检查

```
GET /health
```

检查服务健康状态和模型加载状态。

### 2. 提交生成任务

```
POST /api/generate
```

提交图像生成任务，返回任务 ID。

**请求参数**：
- `prompt` (必填): 文本提示词
- `height` (可选): 图像高度，默认 1024
- `width` (可选): 图像宽度，默认 1024
- `num_inference_steps` (可选): 推理步数，默认 9
- `seed` (可选): 随机种子

### 3. 查询任务状态

```
GET /api/task/<task_id>
```

查询指定任务的状态和详细信息。

### 4. 获取生成结果

```
GET /api/result/<task_id>
```

获取生成的图像文件（任务完成时）。

### 5. 查询系统状态

```
GET /api/status
```

查询系统整体状态，包括队列信息、GPU 使用情况等。

详细 API 文档请参考后台服务的 README.md。

## 常见问题

### 1. 连接后台失败怎么办？

- 检查后台服务是否已启动
- 检查后台服务地址配置是否正确
- 检查网络连接是否正常
- 检查防火墙设置
- 使用"测试连接"功能验证配置

### 2. 生成失败的常见原因

- **队列已满**：等待队列中的任务完成后再试
- **模型未加载**：检查后台服务日志，确认模型加载成功
- **GPU 内存不足**：降低图片尺寸或推理步数
- **参数错误**：检查参数是否在允许范围内

### 3. 如何提高生成质量？

- **详细描述**：提供更详细的提示词描述
- **增加推理步数**：适当增加 `num_inference_steps`（但会增加生成时间）
- **使用提示词润色**：使用模板或增强功能优化提示词
- **调整图片尺寸**：使用更高的分辨率（但会增加生成时间）

### 4. 任务一直显示"等待中"？

- 检查后台服务是否正常运行
- 查看任务队列位置，如果位置很大可能需要等待较长时间
- 检查是否有其他任务正在处理

### 5. 图片无法预览或下载？

- 检查任务状态是否为"已完成"
- 检查浏览器控制台是否有错误信息
- 尝试刷新页面后重新加载

## 开发说明

### 添加新功能

1. **创建组件**：在 `components/` 目录下创建新组件
2. **添加类型**：在 `types/index.ts` 中添加类型定义
3. **API 调用**：在 `lib/api.ts` 中添加 API 方法
4. **更新页面**：在 `app/page.tsx` 中集成新功能

### 自定义样式

- 修改 `tailwind.config.js` 配置主题
- 修改 `app/globals.css` 调整全局样式
- 使用 Tailwind CSS 工具类进行样式定制

### 构建生产版本

```bash
npm run build
npm start
```

### 一键启动（推荐）

项目根目录提供了 `start.sh` 启动脚本，可以一键打包前台并启动后台和前台服务。

**使用方法**：

1. **赋予执行权限**（首次使用需要）：

```bash
chmod +x start.sh
```

2. **执行启动脚本**：

```bash
./start.sh
```

**脚本功能**：

- ✅ 自动检查环境依赖（Node.js、npm、Python）
- ✅ 自动打包前台应用（`npm run build`）
- ✅ 后台启动 Flask 服务（端口 5000）
- ✅ 后台启动 Next.js 服务（端口 3000）
- ✅ 详细的日志输出和错误处理

**服务地址**：

- 后台服务：http://localhost:5000
- 前台服务：http://localhost:3000

**查看日志**：

```bash
# 查看后台日志
tail -f ../backend.log

# 查看前台日志
tail -f ../frontend.log
```

**停止服务**：

有两种方式停止服务：

**方式一：使用停止脚本（推荐）**

项目根目录提供了 `stop.sh` 停止脚本，可以一键停止后台和前台服务：

```bash
# 赋予执行权限（首次使用需要）
chmod +x stop.sh

# 执行停止脚本
./stop.sh
```

停止脚本功能：
- ✅ 自动查找并停止后台服务（端口 5000）
- ✅ 自动查找并停止前台服务（端口 3000）
- ✅ 支持多种进程查找方式（lsof、netstat、ps）
- ✅ 如果正常停止失败，会自动尝试强制停止
- ✅ 详细的日志输出

**方式二：手动停止**

如果脚本不可用，可以手动停止：

```bash
# 停止后台服务（端口 5000）
lsof -ti:5000 | xargs kill

# 停止前台服务（端口 3000）
lsof -ti:3000 | xargs kill
```

或者使用进程 ID（启动脚本会输出 PID）：

```bash
# 停止后台服务
kill <BACKEND_PID>

# 停止前台服务
kill <FRONTEND_PID>
```

**注意事项**：

- 如果端口已被占用，启动脚本会提示但不会强制停止已有服务
- 脚本会在项目根目录生成日志文件：`backend.log` 和 `frontend.log`
- 确保已安装所有依赖（后台：`pip install -r requirements.txt`，前台：`npm install`）

## 浏览器支持

- Chrome/Edge (最新版本)
- Firefox (最新版本)
- Safari (最新版本)

**注意**：本应用仅支持桌面端浏览器，移动端浏览器会显示阻止页面。

## 许可证

本项目基于 Z-Image-Turbo 模型，请遵循相应的许可证要求。

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

