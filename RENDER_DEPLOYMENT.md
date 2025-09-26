# 🚀 Render部署指南 - SEO AutoPilot

## 快速部署步骤

### 1. 准备GitHub仓库
```bash
# 确保所有更改已提交并推送到GitHub
git add .
git commit -m "🚀 Prepare for Render deployment - Remove ngrok dependencies"
git push origin main
```

### 2. 在Render创建Web服务

1. 访问 [render.com](https://render.com) 并登录
2. 点击 "New +" → "Web Service"
3. 连接你的GitHub仓库
4. 选择 SEO-AutoPilot 项目

### 3. Render服务配置

**基本设置：**
- **Name**: `seo-autopilot`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt && pip install -e .`
- **Start Command**: `python -m pyseoanalyzer.api`
- **Plan**: Free (或根据需要选择付费计划)

**高级设置：**
- **Auto-Deploy**: Yes (推荐)
- **Root Directory**: `/` (保持默认)
- **Health Check Path**: `/api/health`

### 4. 环境变量配置

在Render仪表板中添加以下环境变量：

#### 必需的环境变量：
```
FLASK_ENV=production
PYTHONPATH=/opt/render/project/src
```

#### AI分析API密钥（至少需要一个）：
```
ANTHROPIC_API_KEY=sk-your-anthropic-key-here
SILICONFLOW_API_KEY=sk-your-siliconflow-key-here
```

#### 可选的性能优化配置：
```
CACHE_ENABLED=true
CACHE_TTL=3600
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
LOG_LEVEL=INFO
```

### 5. 部署验证

部署完成后，你的服务将在以下URL可用：
- **Web界面**: `https://your-app-name.onrender.com`
- **API健康检查**: `https://your-app-name.onrender.com/api/health`

#### 测试部署：
```bash
# 测试健康检查
curl https://your-app-name.onrender.com/api/health

# 测试SEO分析
curl -X POST https://your-app-name.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "run_llm_analysis": false}'
```

## 🔧 部署后配置

### 自定义域名（可选）
1. 在Render仪表板中点击 "Settings"
2. 在 "Custom Domains" 部分添加你的域名
3. 配置DNS记录指向Render提供的地址

### SSL证书
Render自动为所有服务提供免费SSL证书，包括自定义域名。

### 监控和日志
- **实时日志**: 在Render仪表板中查看 "Logs" 标签页
- **健康监控**: Render自动监控 `/api/health` 端点
- **性能指标**: 在 "Metrics" 标签页查看CPU、内存使用情况

## 📊 性能优化建议

### 1. 免费计划限制
- **内存**: 512MB
- **构建时间**: 15分钟
- **休眠**: 15分钟无活动后休眠
- **带宽**: 100GB/月

### 2. 生产环境建议
对于生产使用，考虑升级到付费计划：
- **Starter ($7/月)**: 1GB RAM, 不休眠
- **Standard ($25/月)**: 2GB RAM, 更好的性能
- **Pro ($85/月)**: 4GB RAM, 专用资源

### 3. 缓存优化
确保启用缓存以减少API调用成本：
```
CACHE_ENABLED=true
CACHE_TTL=3600  # 1小时缓存
CACHE_MAX_SIZE=1000  # 最大缓存条目
```

## 🛠️ 故障排除

### 常见问题：

#### 1. 构建失败
```bash
# 检查requirements.txt是否完整
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements.txt"
git push
```

#### 2. 启动超时
- 检查 `Start Command` 是否正确: `python -m pyseoanalyzer.api`
- 确保端口绑定正确 (代码已更新为使用 `PORT` 环境变量)

#### 3. API调用失败
- 检查环境变量是否正确设置
- 验证AI API密钥是否有效
- 查看实时日志排查错误

#### 4. 内存不足
- 禁用一些可选功能减少内存使用
- 考虑升级到更高的计划

### 日志分析：
```bash
# 在Render日志中查找关键信息：
# ✅ 成功启动: "🚀 Starting SEO AutoPilot API server on port"
# ✅ 健康检查: "GET /api/health - 200"
# ❌ 错误信息: "ERROR" 或 "Exception"
```

## 🚀 部署完成！

部署成功后，你将拥有：

1. **专业的SEO分析平台**，支持60+SEO因子分析
2. **AI增强分析**，使用Anthropic Claude或SiliconFlow
3. **多格式报告生成**，支持HTML、JSON、CSV、XML
4. **自动XML站点地图生成**
5. **实时进度跟踪**和用户友好界面
6. **全球访问**，通过Render的全球CDN

你的SEO AutoPilot现在可以为全球用户提供专业的SEO分析服务！

---

**技术支持**: 如有部署问题，请查看GitHub Issues或联系开发团队。