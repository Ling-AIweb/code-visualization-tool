# Toast 组件预览说明

## 功能概述
Toast 组件用于在上传失败时显示错误提示，采用主页的设计风格。

## 设计特点

### 1. 视觉设计
- **配色方案**：黑白极简风格，错误时显示红色，成功时显示绿色
- **毛玻璃效果**：使用 `backdrop-blur-md` 实现半透明模糊背景
- **边框样式**：2px 实线边框，圆角设计
- **图标**：使用 lucide-react 图标库

### 2. 动画效果
- **滑入动画**：从右侧滑入，时长 0.3s
- **滑出动画**：向右侧滑出，时长 0.3s
- **平滑过渡**：所有状态变化都有过渡动画

### 3. 交互特性
- **自动关闭**：5秒后自动消失
- **手动关闭**：点击 X 按钮可立即关闭
- **固定位置**：显示在页面右上角，不遮挡主要内容

## 使用场景

### 错误提示
当用户上传失败时，会触发以下错误场景的 Toast 提示：

1. **文件格式错误**
   - 提示：请上传 ZIP 格式的代码压缩包
   - 触发：上传非 ZIP 文件

2. **文件大小超限**
   - 提示：文件大小超过 500MB 限制
   - 触发：上传超过 500MB 的文件

3. **上传失败**
   - 提示：上传失败，请检查网络后重试
   - 触发：网络错误或服务器错误

4. **解析失败**
   - 提示：解析失败，请重试
   - 触发：后端解析任务失败

5. **网络连接中断**
   - 提示：网络连接中断，请重试
   - 触发：轮询状态时网络连接中断

## 代码示例

### Toast 组件结构
```tsx
<Toast
  type="error"  // 'error' | 'success' | 'info'
  message="上传失败，请检查网络后重试"
  onClose={() => setToast(null)}
/>
```

### 在 CodeUploadZone 中使用
```tsx
const [toast, setToast] = useState<{ type: 'error' | 'success' | 'info'; message: string } | null>(null)

// 触发错误提示
setToast({ type: 'error', message: '上传失败，请检查网络后重试' })

// 渲染 Toast
{toast && (
  <Toast
    type={toast.type}
    message={toast.message}
    onClose={() => setToast(null)}
  />
)}
```

## 预览效果

### 错误提示样式
- 背景色：`bg-red-500/90` (红色半透明)
- 边框色：`border-red-500`
- 图标：`AlertCircle` (警告图标)
- 文字颜色：白色

### 成功提示样式
- 背景色：`bg-emerald-500/90` (绿色半透明)
- 边框色：`border-emerald-500`
- 图标：`CheckCircle` (成功图标)
- 文字颜色：白色

### 信息提示样式
- 背景色：`bg-white/90` (白色半透明)
- 边框色：`border-white`
- 文字颜色：白色

## 动画 CSS

```css
@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slide-out {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100%);
  }
}
```

## 测试方法

1. 启动开发服务器：
   ```bash
   cd frontend
   npm run dev
   ```

2. 访问 `http://localhost:5173`

3. 测试错误场景：
   - 上传非 ZIP 文件（如 .txt, .pdf）
   - 上传超过 500MB 的文件
   - 在无网络环境下上传
   - 上传后关闭网络连接

4. 观察右上角的 Toast 提示效果

## 设计一致性

Toast 组件完全遵循主页的设计规范：
- 使用相同的字体：Space Grotesk
- 相同的圆角风格：无圆角 (rounded-none)
- 相同的动画时长：0.3s
- 相同的配色方案：黑白为主，辅以功能色
- 相同的毛玻璃效果：backdrop-blur-md
