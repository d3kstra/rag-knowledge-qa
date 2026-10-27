#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档元数据抽取（确定性正则，不用 LLM）。

背景：模型看到的上下文只有《文件名》+ 正文，不知道文档的层级（制度/细则/办法）、
适用范围（总部/上海/实习/驻场）、是否现行 —— 这些信息本来就在文档头里，但没有传给模型。
把它们抽成结构化元数据，供应用侧注入 chunk 标签，让模型有能力裁决
"上下位文件冲突"（制度 vs 细则）与"主体错配"（总部规定 vs 上海子公司）。

字段与判定（全部确定性）：
  - scope    : 文档头里「> 适用范围：X」的 X，或「## 适用范围」下一行的正文；
              按下方 SCOPE_RULES 归一化为集合（如 ["北京总部","各子公司"]）；解析不到则 []
  - status   : 头部含「现已废止」→ repealed；否则 current
  - year     : 头部「（云启科技 · YYYY 年 ...）」→ int；解析不到则 null
  - doc_type : 按文件名（去数字前缀）命中关键词，**优先级见 DOC_TYPE_RULES**；
              默认「其他」（如 batch5 的「设备保修条款」不含任何受控词 → 其他，如实体现）

doc_type 的优先级（高 → 低）用于后续裁决"上位文件优先"：
  制度 > 办法 > 规定/规则 > 细则 > 指引/说明 > 通知 > other

输出：doc-metadata.json，key = 文件名（不含 .md，与检索结果的 fileName 一致）
"""
import json
import re
from pathlib import Path

EVAL = Path(__file__).parent
CORPUS = EVAL / "corpus"
OUT = EVAL / "doc-metadata.json"

# 适用范围归一化规则：按固定顺序匹配，命中即加入（顺序即确定性来源）
SCOPE_RULES = [
    ("驻场", "驻场人员"),
    ("实习生", "实习生"),
    ("试用期", "试用期员工"),
    ("上海子公司", "上海子公司"),
    ("深圳分公司", "深圳分公司"),
    ("北京总部", "北京总部"),
    ("IT部", "IT部"),
    ("IT 部", "IT部"),
]
# "包含所有主体"的标记：原文出现这些词时追加
ALL_SUBSIDIARY_MARKERS = ("各子公司", "及子公司")

# doc_type 优先级（高 → 低）；顺序即裁决优先级，勿随意调整
DOC_TYPE_RULES = [
    ("制度", "制度"),
    ("办法", "办法"),
    ("规定", "规定"),
    ("规则", "规定"),
    ("细则", "细则"),
    ("指引", "指引"),
    ("说明", "指引"),
    ("通知", "通知"),
]
DEFAULT_DOC_TYPE = "其他"

QUOTE_SCOPE = re.compile(r"^>\s*适用范围[：:]\s*(.+?)\s*$", re.M)
SECTION_SCOPE = re.compile(r"^##\s*适用范围\s*\n+\s*(.+?)\s*$", re.M)
YEAR = re.compile(r"（[^）]*?(\d{4})\s*年")
PREFIX = re.compile(r"^[A-Za-z]*\d+-")   # 01- / M058- / N00- / C07- 之类的前缀


def header_of(text: str, lines: int = 8) -> str:
    """取文档头部（仅前若干行）：元数据只从头部读，避免正文误命中"""
    return "\n".join(text.split("\n")[:lines])


def parse_scope(header: str):
    raw = None
    m = QUOTE_SCOPE.search(header)
    if m:
        raw = m.group(1)
    else:
        m = SECTION_SCOPE.search(header)
        if m:
            raw = m.group(1)
    if not raw:
        return []
    scopes = []
    for keyword, canonical in SCOPE_RULES:
        if keyword in raw and canonical not in scopes:
            scopes.append(canonical)
    if any(marker in raw for marker in ALL_SUBSIDIARY_MARKERS) and "各子公司" not in scopes:
        scopes.append("各子公司")
    return scopes


def parse_status(header: str) -> str:
    return "repealed" if "现已废止" in header else "current"


def parse_year(header: str):
    m = YEAR.search(header)
    return int(m.group(1)) if m else None


def parse_doc_type(stem: str) -> str:
    title = PREFIX.sub("", stem)
    for keyword, canonical in DOC_TYPE_RULES:
        if keyword in title:
            return canonical
    return DEFAULT_DOC_TYPE


def main():
    docs = sorted(p for p in CORPUS.rglob("*.md") if not p.name.startswith("uploaded-ids"))
    metadata, no_scope, no_year, both_missing = {}, 0, 0, 0
    type_counter, status_counter = {}, {}
    for path in docs:
        stem = path.stem
        header = header_of(path.read_text(encoding="utf-8"))
        scope = parse_scope(header)
        year = parse_year(header)
        meta = {
            "scope": scope,
            "status": parse_status(header),
            "year": year,
            "doc_type": parse_doc_type(stem),
        }
        metadata[stem] = meta
        type_counter[meta["doc_type"]] = type_counter.get(meta["doc_type"], 0) + 1
        status_counter[meta["status"]] = status_counter.get(meta["status"], 0) + 1
        if not scope:
            no_scope += 1
        if year is None:
            no_year += 1
        if not scope and year is None:
            both_missing += 1

    json.dump(metadata, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)

    total = len(docs)
    print(f"扫描文档: {total} 篇（已排除 uploaded-ids*.md 登记册）")
    print(f"  scope 可解析: {total - no_scope}/{total} = {(total - no_scope) * 100 // max(1, total)}%")
    print(f"  year  可解析: {total - no_year}/{total} = {(total - no_year) * 100 // max(1, total)}%")
    print(f"  status 分布: {status_counter}")
    print(f"  doc_type 分布: {dict(sorted(type_counter.items(), key=lambda x: -x[1]))}")
    print(f"  scope 与 year 都解析不到: {both_missing} 篇")
    empty_scope = [k for k, v in metadata.items() if not v["scope"]]
    if empty_scope:
        print(f"  scope 为空（前 8 例）: {empty_scope[:8]}")
    print(f"\n已写入 {OUT}")
    print("样例（前 3 篇 + 含子公司的 1 篇 + 废止的 1 篇）:")
    shown = [k for k in list(metadata)[:3]]
    shown += [k for k, v in metadata.items() if "各子公司" in v["scope"]][:1]
    shown += [k for k, v in metadata.items() if v["status"] == "repealed"][:1]
    for k in dict.fromkeys(shown):
        print(f"  {k}: {json.dumps(metadata[k], ensure_ascii=False)}")


if __name__ == "__main__":
    main()
