#!/usr/bin/env python3
"""为 langchain4j 中文文档生成 llms.txt / llms-full.txt（供 LLM 与 AI 助手消费）。

- llms.txt: 站点说明 + 全部页面的 标题 → 路径 索引
- llms-full.txt: 全部页面全文（按目录顺序，页间以分隔线隔离）
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs-zh"
SITE_BASE = "https://docs.langchain4j.dev"  # 占位：实际站点域名未知，用相对路径
FRONT_MATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)

SITE_TITLE = "LangChain4j 中文文档"
SITE_DESC = (
    "LangChain4j 是一个帮助你在 Java 中使用大型语言模型（LLM）的开源库，"
    "提供统一的 API 接入各大 LLM 提供商与向量存储，内置 AI 服务、工具调用、"
    "RAG、聊天记忆等能力。本文档为官方英文文档的简体中文翻译版。"
)


def page_title(md: Path, fallback: str) -> str:
    for line in md.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#\s+(.*)", line)
        if m:
            return m.group(1).strip()
    return fallback


def page_summary(md: Path) -> str:
    """取 H1 之后第一段非空、非链接列表的正文；跳过 admonition 块。"""
    lines = md.read_text(encoding="utf-8").splitlines()
    after = False
    buf: list[str] = []
    skip_adm = False
    for line in lines:
        if line.startswith("# "):
            after = True
            continue
        if not after:
            continue
        if line.strip().startswith("```"):
            break
        if skip_adm:
            if line.strip() and not line[:1].isspace():
                skip_adm = False
            else:
                continue
        if not line.strip():
            if buf:
                break
            continue
        if line.lstrip().startswith("!!!"):
            skip_adm = True
            continue
        if line.lstrip().startswith(("[!>", "#", "- [", "[![", "|")):
            if buf:
                break
            continue
        buf.append(line.strip())
    text = " ".join(buf)
    return text[:160] + ("…" if len(text) > 160 else "")


def ordered_pages() -> list[Path]:
    """与 mkdocs nav 的大致顺序一致：index、intro、get-started、tutorials、integrations、useful-materials。"""
    pages = [p for p in DOCS.rglob("*.md") if p.suffix == ".md"]

    top_order = {"index.md": 0, "intro.md": 1, "latest-release-notes.md": 2, "get-started.md": 3}
    dir_order = {"tutorials": 4, "integrations": 5, "useful-materials": 6}

    def key(p: Path) -> tuple:
        rel = p.relative_to(DOCS)
        parts = rel.parts
        if len(parts) == 1:
            return (top_order.get(parts[0], 7), parts)
        parts = (parts[0], "" if parts[1] == "index.md" else parts[1], *parts[2:])
        return (dir_order.get(parts[0], 7), parts)

    return sorted(pages, key=key)


def url_of(p: Path) -> str:
    rel = p.relative_to(DOCS)
    u = rel.with_suffix(".html").as_posix()
    if u.endswith("index.html"):
        u = u[: -len("index.html")]
    return u or "/"


def render_llms_txt() -> str:
    out = [f"# {SITE_TITLE}", "", SITE_DESC, ""]
    current = ""
    for p in ordered_pages():
        rel = p.relative_to(DOCS)
        section = rel.parts[0] if len(rel.parts) > 1 else ""
        if section != current:
            current = section
            names = {"": "入门", "tutorials": "教程", "integrations": "集成",
                     "useful-materials": "实用资料"}
            out += [f"## {names.get(section, section)}", ""]
        title = page_title(p, rel.stem)
        summary = page_summary(p)
        line = f"- [{title}]({url_of(p)})"
        if summary and rel.name != "index.md":
            line += f" — {summary}"
        out.append(line)
    out.append("")
    return "\n".join(out)


def render_full() -> str:
    out = [f"# {SITE_TITLE} — 完整文档", "", SITE_DESC, ""]
    for p in ordered_pages():
        rel = p.relative_to(DOCS)
        text = FRONT_MATTER.sub("", p.read_text(encoding="utf-8"))
        out.append(f"<!-- ===== 文件: {rel.as_posix()} ===== -->")
        out.append("")
        out.append(text.rstrip())
        out.append("")
    return "\n".join(out)


def main() -> None:
    (ROOT / "llms.txt").write_text(render_llms_txt(), encoding="utf-8")
    (ROOT / "llms-full.txt").write_text(render_full(), encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: /sitemap.xml\n", encoding="utf-8"
    )
    print("llms.txt", (ROOT / "llms.txt").stat().st_size)
    print("llms-full.txt", (ROOT / "llms-full.txt").stat().st_size)


if __name__ == "__main__":
    main()
