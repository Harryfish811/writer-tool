# ✏️ writer-tool

**写作润色 & 错别字检查 CLI 工具**，用 Python 写的命令行工具，支持本地规则检查 + AI 润色。

## 功能

- ✅ **错别字检查** — 基于常见错别字词库 + 正则模式检测
- ✨ **文章润色** — 本地规则润色 / 可接入大模型 API（硅基流动等）
- 🔧 **直接修正** — 一键替换错别字

## 安装

```bash
git clone https://github.com/Harryfish811/writer-tool.git
cd writer-tool
pip install -e .
```

## 使用

```bash
# 检查错别字
writer check "这是一段要检查的文字"

# 润色文章（本地规则）
writer polish "这是一段要润色的文字"

# 直接修正错别字
writer fix "这是一段有错别的文字"

# 从文件读取
writer check -f article.txt

# 指定润色风格
writer polish -f article.txt --style formal
```

## 润色风格

| 风格 | 说明 |
|------|------|
| `natural` | 自然流畅（默认） |
| `formal` | 书面正式 |
| `casual` | 轻松口语 |
| `literary` | 文学优美 |

## AI 润色配置

使用 AI 润色需要配置 API Key（支持硅基流动等兼容 OpenAI 格式的 API）：

```bash
# 方式一：环境变量
export POLISH_API_KEY="your-api-key"
export POLISH_API_URL="https://api.siliconflow.cn/v1/chat/completions"
export POLISH_MODEL="Qwen/Qwen2.5-7B-Instruct"

# 方式二：直接在代码中填入（不推荐）
```

## 项目结构

```
writer_tool/
├── __init__.py       # 包入口
├── __main__.py       # 模块直接运行入口
├── cli.py            # CLI 界面
├── typo_checker.py   # 错别字检测
├── polisher.py       # 文章润色
```

## License

MIT
