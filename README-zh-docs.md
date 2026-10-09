# LangChain4j 中文文档

[docs.langchain4j.dev](https://docs.langchain4j.dev) 官方英文文档的简体中文翻译版，基于
[mkdocs-material](https://squidfunk.github.io/mkdocs-material/) 构建（与原站 Docusaurus
同款信息架构：左侧全量导航 + 右侧页内目录），样式沿用原站绿色主题与 logo。

站点地址：https://noexcs.github.io/langchain4j-zh/（GitHub Pages 自动部署）

## 目录结构

| 路径 | 说明 |
|---|---|
| `docs-zh/` | 中文 Markdown 源（184 篇源文档 1:1 翻译 + 12 个分类索引页 + 手写总览页），`img/` 为原站图片 |
| `mkdocs.zh.yml` | 构建配置：nav 与原站侧边栏逐条对齐、中文语言、原站绿主题、CJK 标题锚点 slugify |
| `scripts/fix-links-zh.py` | 后处理：内部链接相对化（`.md`/图片）、Docusaurus `/category/` 映射、跨文件锚点按「英文序位 → 译文 → 归一化模糊 → 唯一前缀」映射 |
| `scripts/fix-md-quirks-zh.py` | 后处理：Docusaurus admonition 残留、空 H1 等修正 |
| `scripts/generate-llm-context-zh.py` | 生成 `llms.txt` / `llms-full.txt` / `robots.txt` |
| `build.sh` | 一键构建：生成 LLM 上下文 → `mkdocs build` → 根文件复制到站点根 |
| `serve-docs.sh` | 本地预览（`mkdocs serve`，默认 http://127.0.0.1:8000） |
| `site-zh/` | 构建产物（`.gitignore` 排除，CI 重新构建部署） |

## 构建

```bash
uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt
./build.sh                 # 输出到 site-zh/
./serve-docs.sh            # 本地预览
```

链接采用**相对路径**输出（页面 `.md` 链接由 mkdocs 转 `.html`，图片为相对文件路径），
站点可在任意子路径部署（GitHub Pages 项目站点即子路径）。

翻译/后处理流水线（上游源文档更新时重跑）：

1. 更新英文源：`git -C ~/Projects/langchain4j pull`（upstream 浅克隆，sparse checkout `docs/`）
2. 重新翻译增量页面 → `docs-zh/`
3. `.venv/bin/python scripts/fix-links-zh.py && .venv/bin/python scripts/fix-md-quirks-zh.py`
4. `./build.sh`

## 已知差异

- 原站 8 处链接在英文源文档中本身失效（如 `/tutorials/batch-processing` 官方 404、
  死锚点 `#langchain4j-spring-boot-starter`），译文已改写为指向正确的现有页面/小节。
- 其余锚点均由 `fix-links-zh.py` 映射到译文标题（含 CJK slug，如 `#底层工具-api`）。
- Docusaurus 自动生成的 12 个分类索引页在 mkdocs 中无对应机制，已手写 `index.md`。
- 搜索使用 `lang: zh`（lunr + CJK 分词），中文查询可正常检索。
