# Git 推送代码到 GitHub 操作指南

## 📋 前提条件

1. 已安装 Git
2. 已配置 Git 用户信息（用户名和邮箱）
3. 已在 GitHub 上创建仓库
4. 已将本地仓库与远程仓库关联

---

## 🚀 完整推送流程

### 1. 查看当前状态

```bash
git status
```

**作用**：查看当前有哪些文件被修改、新增或删除

**常见输出**：
```
On branch main
Changes not staged for commit:
  modified:   backend/app/services/vector_service.py
  new file:   backend/app/services/new_feature.py
```

---

### 2. 添加修改的文件到暂存区

#### 方式 1：添加所有修改的文件（推荐）

```bash
git add .
```

**作用**：将所有修改、新增、删除的文件添加到暂存区

#### 方式 2：添加指定文件

```bash
git add backend/app/services/vector_service.py
```

**作用**：只添加指定的文件到暂存区

#### 方式 3：交互式添加

```bash
git add -i
```

**作用**：逐个选择要添加的文件

---

### 3. 提交更改

```bash
git commit -m "提交信息"
```

**提交信息规范**：

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加用户登录功能` |
| `fix` | 修复 bug | `fix: 修复数据库连接失败问题` |
| `docs` | 文档更新 | `docs: 更新 API 文档` |
| `style` | 代码格式调整 | `style: 统一代码缩进` |
| `refactor` | 重构代码 | `refactor: 优化用户服务层` |
| `test` | 测试相关 | `test: 添加单元测试` |
| `chore` | 构建/工具相关 | `chore: 更新依赖版本` |

**示例**：
```bash
git commit -m "feat: 添加 ChromaDB 向量数据库支持"
```

---

### 4. 推送到 GitHub

#### 方式 1：推送到当前分支（常用）

```bash
git push origin main
```

**说明**：
- `origin` - 远程仓库的默认名称
- `main` - 当前分支名称（也可能是 `master`）

#### 方式 2：推送到指定分支

```bash
git push origin feature/new-feature
```

**说明**：推送到名为 `feature/new-feature` 的分支

#### 方式 3：首次推送时设置上游分支

```bash
git push -u origin main
```

**说明**：`-u` 参数会设置上游分支，之后可以直接用 `git push` 推送

---

## 🔍 常见问题排查

### 问题 1：推送失败 - 网络超时

**错误信息**：
```
fatal: unable to access 'https://github.com/xxx/xxx.git/': Recv failure: Operation timed out
```

**解决方案**：

1. **检查网络连接**
```bash
ping github.com
```

2. **增加 Git 超时时间**
```bash
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999
```

3. **使用代理**（如果需要）
```bash
git config --global http.proxy http://proxy.example.com:8080
```

4. **切换到 SSH 方式**
```bash
git remote set-url origin git@github.com:用户名/仓库名.git
```

---

### 问题 2：推送被拒绝 - 远程有更新

**错误信息**：
```
! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'https://github.com/xxx/xxx.git'
```

**原因**：远程仓库有新的提交，本地没有同步

**解决方案**：

1. **先拉取远程更新**
```bash
git pull origin main
```

2. **如果有冲突，解决冲突后重新提交**
```bash
git add .
git commit -m "解决冲突"
git push origin main
```

---

### 问题 3：认证失败

**错误信息**：
```
fatal: Authentication failed for 'https://github.com/xxx/xxx.git/'
```

**解决方案**：

1. **使用 Personal Access Token**
   - GitHub → Settings → Developer settings → Personal access tokens
   - 生成新 token，复制 token

2. **推送时输入凭证**
```bash
git push origin main
# 用户名：GitHub 用户名
# 密码：Personal Access Token
```

3. **配置 Git 凭证存储**
```bash
git config --global credential.helper store
```

---

### 问题 4：分支名称错误

**错误信息**：
```
error: src refspec main does not match any
```

**原因**：当前分支名称不是 `main`

**解决方案**：

1. **查看当前分支名称**
```bash
git branch
```

2. **使用正确的分支名称推送**
```bash
git push origin master  # 如果分支是 master
```

---

## 📝 快速参考

### 日常开发流程（最常用）

```bash
# 1. 查看修改
git status

# 2. 添加所有修改
git add .

# 3. 提交
git commit -m "feat: 添加新功能"

# 4. 推送
git push origin main
```

### 完整工作流示例

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 创建新分支（可选）
git checkout -b feature/new-feature

# 3. 修改代码...

# 4. 查看修改
git status

# 5. 添加修改
git add .

# 6. 提交
git commit -m "feat: 实现新功能"

# 7. 推送到远程分支
git push -u origin feature/new-feature

# 8. 创建 Pull Request（在 GitHub 网页操作）
```

---

## 🔧 常用 Git 命令速查

| 命令 | 说明 |
|------|------|
| `git status` | 查看工作区状态 |
| `git add .` | 添加所有修改到暂存区 |
| `git commit -m "msg"` | 提交更改 |
| `git push origin main` | 推送到远程 |
| `git pull origin main` | 拉取远程更新 |
| `git branch` | 查看本地分支 |
| `git checkout -b branch-name` | 创建并切换到新分支 |
| `git log --oneline -5` | 查看最近 5 条提交记录 |
| `git diff` | 查看未暂存的修改 |
| `git diff --staged` | 查看已暂存的修改 |

---

## 💡 最佳实践

1. **提交前先拉取**：避免冲突
   ```bash
   git pull origin main
   ```

2. **频繁提交**：小步快跑，便于回滚
   ```bash
   git commit -m "fix: 修复拼写错误"
   ```

3. **使用有意义的提交信息**：便于代码审查
   ```bash
   git commit -m "feat: 添加用户登录功能 (#123)"
   ```

4. **定期推送**：避免本地代码丢失
   ```bash
   git push origin main
   ```

5. **使用 `.gitignore`**：避免提交不必要的文件
   ```
   node_modules/
   .env
   __pycache__/
   *.pyc
   ```

---

## 📚 相关资源

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub 官方文档](https://docs.github.com/)
- [Git 提交信息规范](https://www.conventionalcommits.org/)

---

**提示**：遇到问题时，可以使用 `git --help` 查看命令帮助，或在 Stack Overflow 搜索错误信息。
