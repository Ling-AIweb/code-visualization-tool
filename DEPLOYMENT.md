# 免费部署指南 - Vercel + Render

本指南将帮助你将代码可视化工具免费部署到公网，让其他用户可以通过链接访问。

## 📋 部署方案

- **前端**: Vercel（完全免费）
- **后端**: Render（免费套餐）

## 🚀 部署步骤

### 第一步：准备 GitHub 仓库

1. **将代码推送到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/your-username/your-repo.git
   git push -u origin main
   ```

---

### 第二步：部署后端到 Render

1. **访问 Render**
   - 打开 https://render.com
   - 注册/登录账号

2. **创建新的 Web Service**
   - 点击 "New" → "Web Service"
   - 连接你的 GitHub 仓库
   - 选择 `backend` 目录作为根目录

3. **配置服务**
   - **Name**: `code-viz-backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **配置环境变量**
   在 "Advanced" → "Environment Variables" 中添加：
   
   | 变量名 | 值 | 说明 |
   |--------|-----|------|
   | `API_KEY` | `sk-5Ke79wdn8pr7iRlXskZPudyXPgXrUN638lx2snPhTIqqUKc1` | API 密钥 |
   | `API_BASE` | `https://new.lemonapi.site/v1` | API 基础地址 |
   | `MODEL_NAME` | `gemini-2.5-pro` | 模型名称 |
   | `PORT` | `8000` | 端口号 |

5. **部署**
   - 点击 "Create Web Service"
   - 等待部署完成（约 3-5 分钟）
   - 复制生成的后端 URL（例如：`https://code-viz-backend.onrender.com`）

6. **保持后端活跃**
   - Render 免费套餐会在 15 分钟无请求后休眠
   - 可以使用 https://uptimerobot.com 设置定时 ping 保持活跃

---

### 第三步：部署前端到 Vercel

1. **访问 Vercel**
   - 打开 https://vercel.com
   - 注册/登录账号

2. **导入项目**
   - 点击 "Add New" → "Project"
   - 选择你的 GitHub 仓库

3. **配置项目**
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. **配置环境变量**
   在 "Environment Variables" 中添加：
   
   | 变量名 | 值 | 说明 |
   |--------|-----|------|
   | `VITE_API_BASE_URL` | `https://your-backend-url.onrender.com/api` | 后端 API 地址（替换为你的实际后端 URL） |

5. **部署**
   - 点击 "Deploy"
   - 等待部署完成（约 1-2 分钟）
   - 复制生成的前端 URL

---

### 第四步：配置 CORS

**重要**：需要修改后端的 CORS 配置，允许前端域名访问。

1. 在 Render 控制台中，找到你的后端服务
2. 添加环境变量：
   - `CORS_ORIGINS`: `https://your-frontend-url.vercel.app`
3. 重启后端服务

---

## ✅ 验证部署

1. **访问前端**
   - 打开你的 Vercel 前端 URL
   - 测试上传代码功能

2. **检查后端**
   - 访问 `https://your-backend-url.onrender.com/health`
   - 应该返回 `{"status":"healthy"}`

3. **测试完整流程**
   - 上传一个代码压缩包
   - 查看架构可视化效果
   - 测试群聊剧本功能

---

## 🔧 常见问题

### 1. 后端休眠问题

Render 免费套餐会在 15 分钟无请求后休眠，首次访问可能需要 30-60 秒启动。

**解决方案**：
- 使用 Uptime Robot 等工具定时 ping
- 或升级到付费套餐

### 2. CORS 错误

如果前端无法访问后端 API，检查：
- 后端 `CORS_ORIGINS` 是否包含前端 URL
- 前端 `VITE_API_BASE_URL` 是否正确

### 3. 文件上传大小限制

Render 免费套餐对请求大小有限制，建议：
- 上传的代码包不超过 10MB
- 或升级到付费套餐

### 4. ChromaDB 数据持久化

Render 免费套餐重启后会丢失数据。

**解决方案**：
- 使用 Render 的 Disk 功能（已在 `render.yaml` 中配置）
- 或使用云数据库服务

---

## 📊 费用说明

| 服务 | 免费额度 | 说明 |
|------|----------|------|
| Vercel | 完全免费 | 无限带宽，100GB/月 |
| Render | 750 小时/月 | 足够日常使用 |
| **总计** | **$0/月** | 完全免费 |

---

## 🎉 完成！

现在你的代码可视化工具已经部署到公网，其他用户可以通过链接访问了！

**分享链接**：
- 前端：`https://your-frontend-url.vercel.app`
- 后端：`https://your-backend-url.onrender.com`

---

## 📝 后续优化建议

1. **添加自定义域名**
   - Vercel 和 Render 都支持自定义域名
   - 需要购买域名并配置 DNS

2. **升级套餐**
   - 如果需要更多功能，可以升级到付费套餐
   - Render Starter: $7/月
   - Vercel Pro: $20/月

3. **监控和日志**
   - 配置错误监控（如 Sentry）
   - 查看部署日志

4. **性能优化**
   - 添加 CDN 加速
   - 优化图片和静态资源

---

**需要帮助？** 如果在部署过程中遇到问题，可以查看：
- [Vercel 文档](https://vercel.com/docs)
- [Render 文档](https://render.com/docs)
