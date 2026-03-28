# 问财股票监控 - GitHub Actions 部署指南

## 🚀 快速部署 (3 分钟完成)

### 步骤 1: 创建 GitHub 仓库
1. 打开 [GitHub](https://github.com)
2. 点击右上角 **+** -> **New repository**
3. 仓库名：`wencai-monitor` (或任意)
4. 勾选 **Add a README file** (可选)
5. 点击 **Create repository**

### 步骤 2: 上传文件
将以下文件上传到仓库根目录：
- `.github/workflows/wencai-monitor.yml`
- `scripts/wencai_cloud.py`
- `requirements.txt`
- `.gitignore`

**方法 A (推荐)**: 使用 GitHub 网页上传
- 点击 **Add file** -> **Upload files**
- 拖拽上述文件到上传区域
- 点击 **Commit changes**

**方法 B**: 使用 Git 命令行
```bash
git clone https://github.com/你的用户名/wencai-monitor.git
cd wencai-monitor
# 复制上述文件到对应目录
git add .
git commit -m "Initial commit"
git push
```

### 步骤 3: 启用 Actions
1. 进入仓库，点击 **Actions** 标签
2. 如果显示 "Workflows are disabled"，点击 **I understand my workflows, go ahead and enable them**
3. 确保 `wencai-monitor.yml` 已启用（默认自动启用）

### 步骤 4: 查看运行结果
1. 点击 **Actions** -> `问财股票监控 (全自动)`
2. 等待首次运行（每 1 分钟触发一次，或手动点击 **Run workflow**）
3. 运行成功后，点击 **wencai_data.csv** 下载数据

### 步骤 5 (可选): 配置 Telegram 通知
1. 创建 Telegram Bot:
   - 搜索 `@BotFather`
   - 发送 `/newbot`，按提示创建
   - 获取 **Token**
2. 获取 Chat ID:
   - 搜索 `@userinfobot`
   - 发送任意消息，获取 **Chat ID**
3. 在 GitHub 仓库设置中添加密钥:
   - 进入仓库 -> **Settings** -> **Secrets and variables** -> **Actions**
   - 点击 **New repository secret**
   - 添加 `TELEGRAM_BOT_TOKEN` = 你的 Token
   - 添加 `TELEGRAM_CHAT_ID` = 你的 Chat ID

## 📊 数据说明
- **文件**: `wencai_data.csv`
- **内容**: 每 1 分钟自动追加一行数据
- **列**: 代码、名称、现价、涨跌幅、5日涨幅、采集时间
- **下载**: 每次运行后，可在 **Actions** -> **Artifacts** 中下载

## ⚠️ 注意事项
1. **首次运行可能需要 2-3 分钟** (下载 ChromeDriver 等依赖)
2. **问财反爬**: 如果数据为空，可能是 IP 被临时限制，等待几分钟后重试
3. **免费额度**: GitHub Actions 免费用户每月 2000 分钟，本脚本每 1 分钟运行一次，约需 43200 分钟/月，**超出部分需升级或降低频率**
   - **建议修改**: 将 `cron: '*/1 * * * *'` 改为 `cron: '*/5 * * * *'` (每 5 分钟) 以节省额度

## 🛠️ 故障排查
- **运行失败**: 查看 **Actions** 中的日志，点击具体运行 -> **Run job** -> 查看详细错误
- **数据为空**: 检查问财页面是否变化，或尝试修改 `QUERY` 参数
- **超时**: 增加 `WebDriverWait` 的超时时间

## 📞 支持
如有问题，请查看日志或联系开发者。

---
*最后更新: 2026-03-28*
