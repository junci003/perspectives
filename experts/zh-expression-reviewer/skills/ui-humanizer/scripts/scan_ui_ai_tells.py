#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan_ui_ai_tells.py —— 扫描前端项目里的「AI 味」硬指纹。零依赖（仅标准库）。

用法:
    python scan_ui_ai_tells.py <项目目录> [--json out.json] [--top 5]
    python scan_ui_ai_tells.py <项目目录> --quiet --gate --threshold 45   # CI 拦截

退出码:
    0 = 完成（未开启 gate 时恒为 0）
    1 = gate 开启且总分 > threshold
    2 = 参数/路径错误

设计说明（重要）:
    本脚本只覆盖 SKILL.md 里的「三类硬指纹 + 两项几何量化」。
    软指纹（布局默认度、文案占位感、动效同款）需要人工判断，脚本不猜。
    总分是**排序工具**，不是判决书；判断标准始终是「这个界面上有没有
    一处只有这个产品会做的决定」。
"""

import argparse
import json
import os
import re
import sys

try:  # Windows 控制台默认 GBK，中文输出会炸
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", ".nuxt", "out",
    "vendor", "coverage", ".cache", "__pycache__", ".venv", "venv",
    "public", "static", "assets",
}
EXTS = {
    ".html", ".htm", ".css", ".scss", ".less", ".sass",
    ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".astro",
}

# ---------- 指纹定义 ----------

AI_HEX = {
    "#6366f1": "indigo-500", "#4f46e5": "indigo-600", "#4338ca": "indigo-700",
    "#818cf8": "indigo-400", "#8b5cf6": "violet-500", "#7c3aed": "violet-600",
    "#a855f7": "purple-500", "#c084fc": "purple-400", "#ec4899": "pink-500",
    "#f472b6": "pink-400", "#06b6d4": "cyan-500", "#14b8a6": "teal-500",
}
AI_TW_CLASS = re.compile(r"\b(?:from|via|to|bg|text|border|ring|shadow|fill|stroke)-"
                         r"(indigo|violet|purple|fuchsia|pink)-\d{3}\b")
GRADIENT_TW = re.compile(r"\bfrom-\w+-\d{2,3}\b[\s\S]{0,80}?\bto-\w+-\d{2,3}\b")
GRADIENT_CSS = re.compile(r"linear-gradient\(\s*\d{2,3}deg\s*,[^)]*\)")
GRADIENT_3STOP = re.compile(r"linear-gradient\([^)]*\bvia\b|linear-gradient\([^)]*,[^)]*,[^)]*,[^)]*\)")

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF"
    "\U00002600-\U000027BF\U0001F1E6-\U0001F1FF"
    "\u2b00-\u2bff\u2190-\u21ff\u2300-\u23ff\ufe0f]+"
)
# emoji 出现在这些位置时按「承担图标职能」计
ICON_CTX = re.compile(r"<[A-Za-z][\w.-]*|class(Name)?=|:class=|\balt=|\btitle=")

TECH_LEAK = [
    (re.compile(r"\balert\("), "alert() 直接弹原始错误"),
    (re.compile(r"\[object Object\]"), "[object Object] 泄漏"),
    (re.compile(r"\bFailed to fetch\b", re.I), "Failed to fetch 英文报错"),
    (re.compile(r"\bNetworkError\b"), "NetworkError 英文报错"),
    (re.compile(r"net::ERR_"), "net::ERR_ 浏览器底层错误"),
    (re.compile(r"\b(?:TypeError|ReferenceError|SyntaxError)\b"), "JS 异常类名暴露"),
    (re.compile(r"\bCORS\b"), "CORS 术语暴露"),
    (re.compile(r"timeout of \d+ms exceeded"), "axios 超时原文"),
    (re.compile(r">\s*(?:undefined|null|NaN)\s*<"), "渲染出 undefined/null/NaN"),
    (re.compile(r"\bTODO\b|Lorem ipsum"), "占位文本残留"),
]
# 这些是开发期合理内容，命中不计
DEV_ALLOW = re.compile(r"console\.(log|error|warn|debug)|import\.meta\.env\.DEV|process\.env\.NODE_ENV")

PLACEHOLDER = [
    (re.compile(r"\bWelcome to\b", re.I), "Welcome to ..."),
    (re.compile(r"\bGet Started\b", re.I), "Get Started"),
    (re.compile(r"\bLearn More\b", re.I), "Learn More"),
    (re.compile(r"\bAll[- ]in[- ]One\b", re.I), "All-in-One"),
    (re.compile(r"\bSupercharge\b|\bEffortlessly\b|\bSeamlessly\b|\bCutting[- ]Edge\b|\bNext[- ]Generation\b", re.I),
     "英文营销套话"),
    (re.compile(r"赋能|一站式|闭环|抓手|革新"), "中文体制话术"),
    (re.compile(r"让[^。，,]{1,12}更简单|为[^。，,]{1,10}而生|重新定义"), "中文营销套话"),
    (re.compile(r"请稍后重试"), "无信息错误提示"),
    (re.compile(r"\bI'?m a passionate\b", re.I), "I'm a passionate ..."),
]
NO_DATA = re.compile(r"暂无数据|No data|Nothing here")

RADIUS_TW = re.compile(r"\brounded(-t|-b|-l|-r|-tl|-tr|-bl|-br)?-(none|sm|md|lg|xl|2xl|3xl|full)\b")
RADIUS_CSS = re.compile(r"border-radius:\s*([^;]+);")
SHADOW_TW = re.compile(r"\bshadow-(sm|md|lg|xl|2xl|inner|none)\b")
SHADOW_CSS = re.compile(r"box-shadow:\s*([^;]+);")

CATEGORIES = [
    ("color", "AI 默认色板", 25),
    ("gradient", "渐变签名", 15),
    ("emoji", "emoji 当图标", 20),
    ("leak", "技术信息泄漏", 20),
    ("placeholder", "占位 / 套话文案", 10),
    ("radius", "圆角无层级", 5),
    ("shadow", "阴影无差别", 5),
]


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in EXTS:
                yield os.path.join(dirpath, fn)


def scan_text(text):
    """返回 {cat: [(lineno, label, snippet)]}"""
    hits = {k: [] for k, _, _ in CATEGORIES}
    radius_vals, shadow_vals = [], []

    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        stripped = line.strip()
        # 注释行不算指纹（注释里出现 "Failed to fetch" 是文档，不是泄漏）
        is_comment = (
            stripped.startswith(("//", "*", "/*", "#", "<!--"))
            or stripped.startswith("--")
        )
        # 色板
        for hexv, name in AI_HEX.items():
            if hexv in low:
                hits["color"].append((i, f"{hexv} ({name})", line.strip()[:100]))
        for m in AI_TW_CLASS.finditer(line):
            hits["color"].append((i, m.group(0), line.strip()[:100]))
        # 渐变
        for rx, lbl in ((GRADIENT_TW, "Tailwind 渐变"), (GRADIENT_CSS, "CSS 渐变")):
            for m in rx.finditer(line):
                hits["gradient"].append((i, lbl, m.group(0).strip()[:110]))
        if GRADIENT_3STOP.search(line):
            hits["gradient"].append((i, "三色及以上渐变", line.strip()[:110]))
        # emoji 当图标
        for m in EMOJI.finditer(line):
            if ICON_CTX.search(line) and not is_comment:
                hits["emoji"].append((i, m.group(0), line.strip()[:100]))
        # 技术泄漏
        if not DEV_ALLOW.search(line) and not is_comment:
            for rx, lbl in TECH_LEAK:
                if rx.search(line):
                    hits["leak"].append((i, lbl, line.strip()[:110]))
        # 占位文案
        if not is_comment:
            for rx, lbl in PLACEHOLDER:
                if rx.search(line):
                    hits["placeholder"].append((i, lbl, line.strip()[:110]))
            if NO_DATA.search(line) and not ICON_CTX.search(line):
                hits["placeholder"].append((i, "「暂无数据」类空状态", line.strip()[:110]))
        # 几何
        for m in RADIUS_TW.finditer(line):
            radius_vals.append(m.group(0))
        for m in RADIUS_CSS.finditer(line):
            radius_vals.append(m.group(1).strip())
        for m in SHADOW_TW.finditer(line):
            shadow_vals.append(m.group(0))
        for m in SHADOW_CSS.finditer(line):
            shadow_vals.append(m.group(1).strip()[:40])
        # 圆角全站同款
        if re.search(r"border-radius:\s*(1[6-9]|[2-9]\d)px", line):
            hits["radius"].append((i, "大面积容器用大圆角(>=16px)", line.strip()[:100]))
        if re.search(r"rounded-(2xl|3xl)", line) and ("w-full" in line or "h-full" in line or "<section" in line):
            hits["radius"].append((i, "大面积容器用大圆角", line.strip()[:100]))

    # 圆角档数 / 阴影无差别：靠全局统计，挂在 radius/shadow 分类上
    uniq_radius = sorted(set(radius_vals))
    if len(uniq_radius) == 1 and len(radius_vals) >= 8:
        hits["radius"].append((0, f"全站只有 1 档圆角（{uniq_radius[0]}，共 {len(radius_vals)} 处）", ""))
    uniq_shadow = sorted(set(shadow_vals))
    if len(uniq_shadow) == 1 and len(shadow_vals) >= 5:
        hits["shadow"].append((0, f"全站只有 1 档阴影（{uniq_shadow[0]}，共 {len(shadow_vals)} 处）", ""))
    elif len([s for s in uniq_shadow if "lg" in s or "xl" in s]) >= 2 and len(shadow_vals) >= 6:
        hits["shadow"].append((0, f"大阴影铺开（{len(shadow_vals)} 处 / {len(uniq_shadow)} 档）", ""))
    return hits, uniq_radius, uniq_shadow


def sat(n, k=6.0):
    """饱和函数：0 -> 0，越大越接近 1，不惩罚大项目。"""
    return n / (n + k) if n > 0 else 0.0


def main():
    ap = argparse.ArgumentParser(description="扫描前端项目里的 AI 味硬指纹")
    ap.add_argument("path")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--top", type=int, default=3, help="每类展示前 N 条（默认 3）")
    ap.add_argument("--quiet", action="store_true", help="只输出总分")
    ap.add_argument("--gate", action="store_true", help="总分超阈值时以退出码 1 结束")
    ap.add_argument("--threshold", type=float, default=45.0)
    a = ap.parse_args()

    if not os.path.isdir(a.path):
        print(f"错误：不是目录 -> {a.path}", file=sys.stderr)
        return 2

    files = list(iter_files(a.path))
    if not files:
        print(f"错误：{a.path} 下没有可扫描的前端文件（扩展名白名单：{' '.join(sorted(EXTS))}）",
              file=sys.stderr)
        return 2

    total = {k: [] for k, _, _ in CATEGORIES}
    uniq_r_all, uniq_s_all = set(), set()
    per_file = {}

    for p in files:
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        h, ur, us = scan_text(text)
        uniq_r_all.update(ur)
        uniq_s_all.update(us)
        sub = sum(len(v) for v in h.values())
        if sub:
            per_file[os.path.relpath(p, a.path)] = sub
        for k in total:
            total[k].extend([(os.path.relpath(p, a.path),) + t for t in h[k]])

    score = 0.0
    rows = []
    for key, label, weight in CATEGORIES:
        n = len(total[key])
        raw = sat(n) * weight if key not in ("radius", "shadow") else sat(n, 2.0) * weight
        score += raw
        rows.append((label, weight, n, round(raw, 1)))

    score = round(min(score, 100.0), 1)

    if a.quiet:
        print(f"{score:.1f}")
    else:
        print(f"扫描目录：{a.path}")
        print(f"文件数：{len(files)}（跳过 {'/'.join(sorted(SKIP_DIRS)[:6])} 等）")
        print()
        print(f"{'指纹类别':<18}{'权重':>5}{'命中':>6}{'得分':>7}")
        print("-" * 38)
        for label, weight, n, raw in rows:
            print(f"{label:<18}{weight:>5}{n:>6}{raw:>7}")
        print("-" * 38)
        print(f"{'总分':<18}{'':>5}{'':>6}{score:>7}  / 100")
        print()

        print("命中明细：")
        for key, label, _ in CATEGORIES:
            items = total[key]
            if not items:
                continue
            print(f"\n[{label}] 共 {len(items)} 处")
            for f, ln, lbl, snip in items[: a.top]:
                loc = f"{f}:{ln}" if ln else f
                print(f"  {loc}  ·  {lbl}")
                if snip:
                    print(f"      {snip}")
            if len(items) > a.top:
                print(f"  ... 另有 {len(items) - a.top} 处")

        if per_file:
            print("\n按文件（命中数）：")
            for f, n in sorted(per_file.items(), key=lambda x: -x[1])[:10]:
                print(f"  {n:>4}  {f}")

        if uniq_r_all:
            print(f"\n圆角档位：{len(uniq_r_all)} 档 -> {sorted(uniq_r_all)[:10]}")
        if uniq_s_all:
            print(f"阴影档位：{len(uniq_s_all)} 档 -> {sorted(uniq_s_all)[:10]}")
        print("\n提示：总分是排序工具，不是判决书。软指纹（布局默认度 / 文案占位 / 动效同款）"
              "需要人工核对，见 references/visual-tells.md。")

    if a.json_out:
        json.dump(
            {
                "path": a.path,
                "files_scanned": len(files),
                "score": score,
                "categories": [
                    {"key": k, "label": lb, "weight": w, "hits": len(total[k]),
                     "detail": [{"file": f, "line": ln, "label": l, "snippet": s}
                                for f, ln, l, s in total[k]]}
                    for k, lb, w in CATEGORIES
                ],
                "radius_values": sorted(uniq_r_all),
                "shadow_values": sorted(uniq_s_all),
                "per_file": per_file,
            },
            open(a.json_out, "w", encoding="utf-8"),
            ensure_ascii=False, indent=2,
        )
        if not a.quiet:
            print(f"\nJSON 已写入：{a.json_out}")

    if a.gate and score > a.threshold:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
