# PaperSeeker

AI 驱动的学术论文推荐系统

## 概述

PaperSeeker 自动从 [OpenAlex](https://openalex.org) 搜索相关学术论文，使用 LLM 智能筛选相关性，并通过邮件每日推送精选论文。

## 功能特性

- **OpenAlex 集成** - 免费高质量学术论文数据库
- **AI 智能筛选** - 使用 LLM 对论文进行相关性评分和过滤
- **双语摘要** - 自动生成中英文摘要
- **定时推送** - 每日自动邮件送达
- **完全可配置** - 轻松自定义研究兴趣和提示词
- **成本优化** - 关键词预筛选 + LLM 精筛

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
notepad .env
```

在 `.env` 中配置所有 API 凭证：
- `API_KEY` - LLM API 密钥
- `LLM_MODEL` - LLM 模型名称（如 DeepSeek-V3.2）
- `LLM_BASE_URL` - API 端点 URL
- `EMAIL_PASSWORD` - 邮件应用密码（Gmail/163）
- `SENDER_EMAIL` - 发件人邮箱
- `RECIPIENT_EMAIL` - 收件人邮箱
- `SMTP_SERVER` / `SMTP_PORT` - 邮件服务器设置

### 3. 配置搜索设置

```bash
# 复制配置模板
cp config.example.yaml config.yaml

# 编辑配置
nano config.yaml
```

### 4. 定义研究兴趣

```bash
nano prompts.yaml
```

修改 `research_keywords` 以匹配您的研究方向。

### 5. 运行测试

```bash
python -m tests.test_paper_flow
```

### 6. 启动服务

```bash
# 立即运行一次（搜索昨天的论文）
python main.py --run-once

# 指定日期范围
python main.py --run-once --from-date 2025-01-14 --to-date 2025-01-14

# 启动定时推送
python main.py
```

## 项目结构

```
PaperSeeker/
├── config.yaml              # 搜索和调度配置（不提交）
├── prompts.yaml             # 用户可编辑的提示词和关键词
├── requirements.txt         # 依赖列表
├── .env.example             # 环境变量模板
├── .gitignore               # Git 忽略规则
├── src/
│   ├── __init__.py
│   ├── config.py           # 配置管理
│   ├── paper_searcher.py   # OpenAlex 论文搜索
│   ├── paper_filter.py     # 关键词预筛选 + LLM 精筛
│   ├── summarizer.py       # 双语摘要生成
│   ├── email_sender.py     # 邮件发送
│   └── scheduler.py        # 定时任务
├── tests/
│   └── test_paper_flow.py
├── main.py                 # 入口脚本
└── README.md
```

## 配置说明

### 环境变量 (`.env`)

所有敏感凭证和 API 配置都在 `.env` 中：

```bash
# LLM API 配置
API_KEY=your-api-key
LLM_MODEL=DeepSeek-V3.2
LLM_BASE_URL=https://llmapi.paratera.com/v1/

# 邮件配置
EMAIL_PASSWORD=your-app-password
SENDER_EMAIL=your-email@domain.com
RECIPIENT_EMAIL=recipient@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 搜索配置 (`config.yaml`)

```yaml
search:
  max_results: 20          # 每个关键词返回的论文数量
  days_back: 1             # 搜索最近 N 天的论文
  relevance_threshold: 3   # LLM 评分阈值 (1-5)，低于此值的论文被过滤

scheduler:
  trigger_time: "22:00"   # 本地调度器的 UTC 时间
  enabled: true
```

### 提示词配置 (`prompts.yaml`)

```yaml
research_keywords:        # 研究领域关键词列表
  - "关键词1"
  - "关键词2"

exclude_keywords:         # 排除关键词列表
  - "排除词1"

filter_prompt:            # LLM 筛选提示词
summarize_prompt:         # 摘要生成提示词（中英双语）
summarize_threshold: 4    # 生成摘要的阈值 (1-5)
```

## 邮件服务商配置

在 `.env` 中配置 SMTP 设置：

```bash
# Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# 163 邮箱
SMTP_SERVER=smtp.163.com
SMTP_PORT=25
```

## 筛选策略（成本优化）

采用混合筛选策略以优化 API 成本：

1. **预筛选（免费）**：关键词匹配
   - 使用 `prompts.yaml` 中的 `research_keywords`
   - 快速过滤明显不相关的论文

2. **精筛（付费）**：LLM API
   - 只对预筛选后的候选论文调用 API
   - 评分 1-5，保留相关性评分 >= 4 的论文

## 命令行选项

```bash
python main.py --test                    # 运行测试
python main.py --run-once               # 立即运行（搜索昨天的论文）
python main.py --run-once --from-date 2025-01-14 --to-date 2025-01-14
python main.py --send-test-email         # 发送测试邮件
```

## GitHub Actions 自动推送

1. **fork 或克隆此仓库**

2. **在仓库设置中添加 secrets**：Settings → Secrets and variables → Actions：
   - `API_KEY` - LLM API 密钥
   - `EMAIL_PASSWORD` - 邮件应用密码

3. **工作流每日 UTC 22:00 运行**（北京时间次日 06:00）

4. **手动测试**：
   - 进入仓库 → Actions → "PaperSeeker Daily Push"
   - 点击 "Run workflow"

5. **修改推送时间**，编辑 `.github/workflows/workflow.yml`：
   ```yaml
   schedule:
     - cron: '0 22 * * *'  # 改为您偏好的 UTC 时间
   ```

## 依赖

```
openalex>=0.5.0
openai>=1.0.0
apscheduler==3.10.4
pyyaml==6.0.1
python-dotenv==1.0.0
tqdm>=4.66.0
```

## 许可证

MIT
