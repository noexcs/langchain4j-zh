#!/usr/bin/env python3
"""中文文档后处理：内部链接与锚点统一修复。

背景：译文由多个子代理并行翻译，锚点按“小写/空白→连字符/保留 CJK”规则尽力计算，
与 python-markdown toc（slugify_unicode）的最终锚点可能有细微差异。
本脚本以源英文文档与译文档的标题顺序 1:1 对应，重算所有内部锚点。

规则：
1. 内部链接路径：去尾部斜杠、.md→.html、目录→目录/index.html；
   相对 ../ 与绝对 / 均处理；static/img/ → /img/。
2. 锚点：对每个带锚点的链接，在目标页对应英文源文件的标题序列表中查找
   原英文 slug 的位置 i，再把锚点替换为译文第 i 个标题的 slugify_unicode。
   英文 slug 查不到时，依次尝试译文 slug 精确匹配、归一化模糊匹配
   （小写、连字符/下划线折叠）；都失败则保留原样并报告。
3. 代码块（围栏内）一律不动。
4. 标题数量一致性检查：源/译文标题数量不一致的文件列入报告。

用法: python scripts/fix-links-zh.py [--check]   （--check 只报告不修改）
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from markdown.extensions.toc import slugify_unicode

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "docs"
DST = ROOT / "docs-zh"

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE = re.compile(r"^(```|~~~)")
LINK = re.compile(r"\]\(([^()\s]+)\)")
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:")
IMAGE_EXT = re.compile(r"\.(?:svg|png|jpe?g|gif|webp|ico|avif)(?:\.html)?$")


def headings(text: str) -> list[str]:
    """按出现顺序提取代码块外的标题文字。"""
    out = []
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING.match(line)
        if m:
            out.append(m.group(2).strip())
    return out


def unique(slugs: list[str]) -> list[str]:
    """复刻 markdown toc 的重复 id 处理（-1, -2, ...）。"""
    used: dict[str, int] = {}
    out = []
    for s in slugs:
        if s not in used:
            used[s] = 0
            out.append(s)
        else:
            used[s] += 1
            out.append(f"{s}-{used[s]}")
    return out


def load_page(path: Path | None) -> tuple[list[str], list[str]]:
    """返回 (标题列表, 标题 slug 列表)；文件不存在返回空。"""
    if path is None or not path.exists():
        return [], []
    hs = headings(path.read_text(encoding="utf-8"))
    return hs, unique([slugify_unicode(h, "-") for h in hs])


def src_of(zh_rel: str) -> Path | None:
    p = SRC / zh_rel
    if p.exists() and p.suffix in (".md", ".mdx"):
        return p
    if zh_rel.endswith(".md"):
        p_mdx = SRC / (zh_rel[:-3] + ".mdx")
        if p_mdx.exists():
            return p_mdx
    return None


def norm_slug(s: str) -> str:
    return re.sub(r"[-_]+", "-", s.lower()).strip("-")


def resolve_target(base_file: Path, target: str) -> str | None:
    """把链接目标解析为 docs-zh 内的相对 .md 路径；解析不到返回 None。"""
    t = target.split("#", 1)[0].rstrip("/")
    if not t or SCHEME.match(t) or t.startswith("mailto:"):
        return None
    if IMAGE_EXT.search(t):
        return None  # 静态资源，无 .md 目标
    t = t.replace("static/img/", "img/")
    if t.startswith("/category/"):
        # Docusaurus 栏目页 → 对应分类的 index.md
        slug = t[len("/category/"):]
        if slug.endswith(".html"):
            slug = slug[:-5]
        if (DST / "integrations" / slug / "index.md").exists():
            return f"integrations/{slug}/index.md"
        return None
    if t.endswith(".md"):
        t = t[:-3]
    if t.endswith(".html"):
        t = t[:-5]
    if t.startswith("/"):
        bases = [t[1:]]
    else:
        # 先按当前页目录解析；失败再按 docs-zh 根解析（译文存在漏掉
        # 前导 / 的根相对链接，如 integrations/.../x.md 里写 tutorials/rag.md）
        base_rel = os.path.dirname(os.path.relpath(base_file, DST))
        bases = [os.path.normpath(os.path.join(base_rel, t)), os.path.normpath(t)]
    for rel in bases:
        if rel.startswith(".."):
            continue
        if (DST / rel / "index.md").exists():
            return f"{rel}/index.md"
        if (DST / (rel + ".md")).exists():
            return rel + ".md"
    return None


def match_anchor(
    anchor: str,
    en_map: dict[str, int],
    zh_slugs: list[str],
) -> str | None:
    """按 英文序位 → 译文精确 → 归一化模糊 的顺序解析锚点。"""
    if anchor in en_map and en_map[anchor] < len(zh_slugs):
        return zh_slugs[en_map[anchor]]
    if anchor in zh_slugs:
        return anchor
    na = norm_slug(anchor)
    for zs in zh_slugs:
        if norm_slug(zs) == na:
            return zs
    # 唯一前缀兜底：原文档偶有截断锚点（如 #micrometer-observation 指向
    # “Micrometer Observation API”），仅当恰好一个候选 slug 以锚点开头时采用。
    if len(na) >= 8:
        cands = [zs for zs in zh_slugs if norm_slug(zs).startswith(na)]
        if len(cands) == 1:
            return cands[0]
    return None


def rewrite(md_file: Path, check: bool) -> dict:
    rel = os.path.relpath(md_file, DST)
    text = md_file.read_text(encoding="utf-8")
    zh_headings, zh_slugs = load_page(md_file)

    src_headings, src_slugs = load_page(src_of(rel))
    en_map = {s: i for i, s in enumerate(src_slugs)}
    report = {
        "file": rel,
        "fixed": 0,
        "unresolved": [],
        "mismatch": bool(src_headings and len(src_headings) != len(zh_headings)),
    }

    # 目标页缓存: rel_md -> (英文slug→位置, 译文slug列表)
    target_cache: dict[str, tuple[dict[str, int], list[str]]] = {}

    def target_maps(rel_md: str) -> tuple[dict[str, int], list[str]]:
        if rel_md not in target_cache:
            t_en = load_page(src_of(rel_md))[1]
            _t_zh_h, t_zh_s = load_page(DST / rel_md)
            target_cache[rel_md] = ({s: i for i, s in enumerate(t_en)}, t_zh_s)
        return target_cache[rel_md]

    def emit_rel(in_dst: str, anchor: str | None) -> str | None:
        """把 docs-zh 内相对路径 in_dst 转成「相对当前页目录」的链接目标。"""
        rel_dir = os.path.dirname(os.path.relpath(md_file, DST))
        rel_path = os.path.relpath(in_dst, start=rel_dir or ".").replace(os.sep, "/")
        if anchor:
            rel_path = f"{rel_path}#{anchor}"
        return rel_path

    def fix(match: re.Match) -> str:
        target = match.group(1)
        if SCHEME.match(target) or target.startswith("mailto:"):
            return match.group(0)

        # 纯页内锚点
        if target.startswith("#"):
            anchor = target[1:]
            new_anchor = match_anchor(anchor, en_map, zh_slugs)
            if new_anchor is None:
                report["unresolved"].append(target)
                return match.group(0)
            if new_anchor != anchor:
                report["fixed"] += 1
            return f"](#{new_anchor})"

        # 路径 + 可选锚点
        raw, _, anchor = target.partition("#")
        norm = raw.rstrip("/")

        # —— 静态资源（图片等）：输出相对当前页的真实文件路径 ——
        page_dir = os.path.dirname(os.path.relpath(md_file, DST))
        img_in_dst = None
        if "static/img/" in norm:
            img_in_dst = "img/" + norm.split("static/img/", 1)[1]
        elif norm.startswith("/img/"):
            img_in_dst = norm[1:]
        elif re.match(r"^(?:\.\./)+img/", norm):
            # ../img/ 相对当前页目录 → 归一到 docs-zh 根下 img/
            img_in_dst = os.path.normpath(os.path.join(page_dir, norm))
        elif norm.startswith("img/"):
            img_in_dst = norm
        if img_in_dst is not None and IMAGE_EXT.search(img_in_dst):
            img_in_dst = img_in_dst[:-5] if img_in_dst.endswith(".html") else img_in_dst
            if not (DST / img_in_dst).exists():
                report["unresolved"].append(target)
                return match.group(0)
            new_path = emit_rel(img_in_dst, None)
            new_link = f"]({new_path})"
            if new_link != match.group(0):
                report["fixed"] += 1
            return new_link

        # —— 页面链接：解析为 .md，输出相对 .md 路径（mkdocs 会转 .html，
        #    与 conductor 一致，保证子路径 /langchain4j-zh/ 下可部署）——
        rel_md = resolve_target(md_file, raw)
        if rel_md is None:
            report["unresolved"].append(target)
            return match.group(0)
        new_anchor = None
        if anchor:
            ten, tzs = target_maps(rel_md)
            new_anchor = match_anchor(anchor, ten, tzs)
            if new_anchor is None:
                report["unresolved"].append(target)
                return match.group(0)
        new_path = emit_rel(rel_md, new_anchor)
        new_link = f"]({new_path})"
        if new_link != match.group(0):
            report["fixed"] += 1
        return new_link

    out_lines = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        out_lines.append(LINK.sub(fix, line) if not in_fence else line)
    new_text = "".join(out_lines)

    if not check and new_text != text:
        md_file.write_text(new_text, encoding="utf-8")
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    files = sorted(DST.rglob("*.md"))
    total_fixed = 0
    problems = 0
    for f in files:
        r = rewrite(f, args.check)
        total_fixed += r["fixed"]
        if r["mismatch"] or r["unresolved"]:
            problems += 1
            print(f"[{'MISMATCH' if r['mismatch'] else 'UNRESOLVED'}] {r['file']}")
            for u in r["unresolved"][:10]:
                print(f"    {u}")
    print(f"\nfiles: {len(files)}  fixed: {total_fixed}  problem files: {problems}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
