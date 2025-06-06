# NovAgent - 智能小说创作助手

NovAgent 是一个基于 LangGraph 和 Qwen3-235B 的智能小说创作助手，能够帮助用户从零开始创作小说或修改现有作品。

## 主要功能

1. **智能概念生成**
   - 自动生成小说概念，包括标题、类型、主题等
   - 支持用户手动输入或 AI 辅助生成
   - 提供概念修改和确认机制

2. **大纲创作**
   - 基于确认的概念生成详细大纲
   - 支持大纲的修改和优化
   - 提供章节级别的规划

3. **内容生成**
   - 根据大纲生成小说内容
   - 支持分章节生成
   - 提供内容修改和优化功能

4. **本地存储**
   - 自动保存创作内容
   - 支持多版本管理
   - 提供项目恢复功能

## 工作流程

1. **概念收集阶段**
   ```
   用户输入/AI生成 -> 概念确认 -> 修改优化 -> 最终确认
   ```

2. **大纲创作阶段**
   ```
   概念输入 -> 大纲生成 -> 用户确认 -> 修改优化 -> 最终确认
   ```

3. **内容生成阶段**
   ```
   大纲输入 -> 内容生成 -> 用户确认 -> 修改优化 -> 保存
   ```

4. **修改优化阶段**
   ```
   加载已有内容 -> 修改请求 -> 内容更新 -> 保存
   ```

## 环境要求

- Python 3.8+
- 依赖包：
  - langgraph>=0.0.15
  - dashscope>=1.10.0
  - python-dotenv>=1.0.0
  - pydantic>=2.0.0
  - typing-extensions>=4.5.0

## 快速开始

1. 克隆仓库：
   ```bash
   git clone https://github.com/cang-zhu/NovAgent.git
   cd NovAgent
   ```

2. 创建虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   .\venv\Scripts\activate  # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量：
   创建 `.env` 文件并设置以下变量：
   ```
   NOVEL_WORKING_DIR=./novels
   QWEN_MODEL_NAME=qwen3-235b-a22b
   QWEN_API_KEY=你的API密钥
   QWEN_TEMPERATURE=0.7
   QWEN_MAX_TOKENS=2048
   ```

5. 运行程序：
   ```bash
   python novel_agent.py
   ```

## 使用说明

1. **开始新项目**
   - 选择"开始新项目"
   - 选择手动输入或 AI 生成概念
   - 按照提示完成概念确认
   - 进入大纲创作阶段

2. **修改现有项目**
   - 选择"修改现有项目"
   - 选择要修改的项目
   - 选择修改类型（大纲/内容）
   - 进行修改并保存

## 注意事项

- 请确保 API 密钥的安全性
- 建议定期备份创作内容
- 大型项目建议分章节生成
- 修改时注意保持情节连贯性

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证

MIT License 