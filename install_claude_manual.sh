#!/bin/bash

# Claude Code 手动安装脚本
# 适用于 macOS ARM64 (Apple Silicon)

set -e

echo "🚀 开始安装 Claude Code..."

# 版本配置
VERSION="2.1.45"
ARCH="arm64"
PLATFORM="darwin"

# 下载 URL
DOWNLOAD_URL="https://github.com/anthropics/claude-code/releases/download/v${VERSION}/claude-code-${PLATFORM}-${ARCH}"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
echo "📁 创建临时目录: $TEMP_DIR"

# 下载二进制文件
echo "⬇️  正在下载 Claude Code v${VERSION} (${PLATFORM}-${ARCH})..."
curl -L -o "${TEMP_DIR}/claude" "${DOWNLOAD_URL}"

# 验证下载
if [ ! -f "${TEMP_DIR}/claude" ]; then
    echo "❌ 下载失败！"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 设置可执行权限
chmod +x "${TEMP_DIR}/claude"

# 创建目标目录
mkdir -p ~/.local/bin

# 移动二进制文件
echo "📦 安装到 ~/.local/bin/claude"
mv "${TEMP_DIR}/claude" ~/.local/bin/claude

# 清理临时目录
rm -rf "$TEMP_DIR"

# 检查 PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "⚠️  警告: ~/.local/bin 不在您的 PATH 中"
    echo ""
    echo "请将以下内容添加到您的 shell 配置文件中 (~/.zshrc):"
    echo ""
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "然后运行: source ~/.zshrc"
fi

echo ""
echo "✅ Claude Code 安装完成！"
echo ""
echo "运行以下命令启动:"
echo "    cd your-project"
echo "    claude"
echo ""
