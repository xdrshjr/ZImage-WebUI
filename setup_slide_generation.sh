#!/bin/bash
# Slide生成服务安装脚本
# 用于快速安装Slide生成所需的所有依赖

set -e

echo "=========================================="
echo "Slide生成服务 - 依赖安装脚本"
echo "=========================================="
echo ""

# 检查Python版本
echo "检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"
echo ""

# 安装slide-gen依赖
echo "安装slide-gen依赖..."
pip install -r slide-gen/requirements.txt
echo "✓ slide-gen依赖安装完成"
echo ""

# 安装Playwright浏览器
echo "安装Playwright Chromium浏览器..."
echo "注意: 需要下载约150MB文件，可能需要一些时间..."
playwright install chromium
echo "✓ Playwright浏览器安装完成"
echo ""

# 检查配置文件
echo "检查配置文件..."
if [ -f ".env" ]; then
    echo "✓ 找到.env配置文件"
    
    # 检查必需的配置项
    missing_configs=()
    
    if ! grep -q "SLIDE_LLM_API_KEY=" .env || grep -q "SLIDE_LLM_API_KEY=$" .env || grep -q "SLIDE_LLM_API_KEY=\"\"" .env; then
        missing_configs+=("SLIDE_LLM_API_KEY")
    fi
    
    if ! grep -q "SLIDE_IMAGE_API_KEY=" .env || grep -q "SLIDE_IMAGE_API_KEY=$" .env || grep -q "SLIDE_IMAGE_API_KEY=\"\"" .env; then
        missing_configs+=("SLIDE_IMAGE_API_KEY")
    fi
    
    if ! grep -q "SLIDE_IMAGE_API_URL=" .env || grep -q "SLIDE_IMAGE_API_URL=$" .env || grep -q "SLIDE_IMAGE_API_URL=\"\"" .env; then
        missing_configs+=("SLIDE_IMAGE_API_URL")
    fi
    
    if [ ${#missing_configs[@]} -gt 0 ]; then
        echo ""
        echo "⚠ 警告: 以下必需配置项未设置或为空:"
        for config in "${missing_configs[@]}"; do
            echo "  - $config"
        done
        echo ""
        echo "请在.env文件中配置这些项目，例如:"
        echo ""
        echo "SLIDE_LLM_API_KEY=your-openai-api-key"
        echo "SLIDE_IMAGE_API_KEY=your-image-api-key"
        echo "SLIDE_IMAGE_API_URL=http://localhost:5000"
        echo ""
    else
        echo "✓ 所有必需配置项已设置"
    fi
else
    echo "⚠ 未找到.env文件"
    echo ""
    echo "请在项目根目录创建.env文件并配置以下必需项:"
    echo ""
    echo "SLIDE_LLM_API_KEY=your-openai-api-key"
    echo "SLIDE_IMAGE_API_KEY=your-image-api-key"
    echo "SLIDE_IMAGE_API_URL=http://localhost:5000"
    echo ""
fi

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "下一步:"
echo "1. 确保.env文件中已配置必需的API密钥"
echo "2. 启动服务: python app.py"
echo "3. 查看日志确认Slide生成服务初始化成功"
echo ""


