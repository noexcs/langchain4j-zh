#!/usr/bin/env python3
"""中文文档渲染兼容性修正（幂等，可重复运行）。

1. admonition 指令行（!!! note 等）后紧跟的空行会终止 MkDocs blockquote，
   导致 note 渲染为空、后续正文脱离 admonition——删除该空行。
2. 三个对比表 index 页（源文件用 Docusaurus `title:` front matter 渲染 H1，
   翻译契约删除了 front matter）补 H1 标题。
"""

from __future__ import annotations

import re
from pathlib import Path

DST = Path(__file__).resolve().parent.parent / "docs-zh"

INDEX_TITLES = {
    "integrations/chat-memory-stores/index.md": "# 所有受支持的聊天记忆存储对比表",
    "integrations/embedding-stores/index.md": "# 所有受支持的向量存储对比表",
    "integrations/language-models/index.md": "# 所有受支持的语言模型对比表",
}


def main() -> None:
    for rel, h1 in INDEX_TITLES.items():
        p = DST / rel
        text = p.read_text(encoding="utf-8")
        if not re.match(r"^# ", text):
            p.write_text(f"{h1}\n\n{text}", encoding="utf-8")
            print("H1 added:", rel)

    fixed = 0
    for p in sorted(DST.rglob("*.md")):
        lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
        out: list[str] = []
        i = 0
        changed = False
        while i < len(lines):
            out.append(lines[i])
            if re.match(r"^!!!\s*(note|tip|info|warning|caution|danger)\b", lines[i]) and i + 1 < len(lines) and lines[i + 1].strip() == "":
                i += 1
                changed = True
            i += 1
        if changed:
            p.write_text("".join(out), encoding="utf-8")
            fixed += 1
            print("admonition fixed:", p.relative_to(DST))
    print("admonition files fixed:", fixed)


if __name__ == "__main__":
    main()
