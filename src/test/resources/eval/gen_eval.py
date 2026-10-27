#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成层评估：答案正确性 / 忠实度 / 答案相关性

设计原则（与项目既有评测保持一致）：
  1) 确定性指标优先——不依赖 judge，可复现；
  2) judge 指标单独一层——LLM 判分有波动，只作为补充信号；
  3) 上下文用**磁盘语料**按 retrievedFiles 重建——不依赖 Milvus，离线可跑。

三类指标：
  A. 正确性 correctness
     - factRecall（确定性）：期望事实命中率（来自结果文件）
     - 多余数字（确定性）：答案里出现、但既不在期望事实也不在检索文档中的数字 → 幻觉嫌疑
     - judgeCorrectness（judge）：对照期望事实给 0-3 分
  B. 忠实度 faithfulness
     - numberGrounding（确定性）：答案里的数字有多少能在检索到的文档原文中找到
     - citationValidity（确定性）：答案里《X》引用是否都在检索到的文档集合内
     - judgeFaithfulness（judge）：逐条论断是否被检索文档支撑，0-3 分 + 无据论断清单
  C. 相关性 relevance
     - judgeRelevance（judge）：是否回答了问题，0-3 分

用法：
  python3 gen_eval.py --results results/xxx.json [--judge] [--model qwen-plus] [--limit N]
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus"
RESULTS = HERE / "results"

DASH_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

# ---------- 语料 ----------

def load_corpus() -> dict:
    """fileName(stem) → 全文。语料是平铺的 md。"""
    idx = {}
    for p in CORPUS.rglob("*.md"):
        try:
            idx[p.stem] = p.read_text(encoding="utf-8")
        except Exception:
            continue
    return idx


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s or "")


# ---------- 确定性指标 ----------

NUM_RE = re.compile(r"\d+(?:\.\d+)?")
CITE_RE = re.compile(r"《([^》]{2,30})》")
# 排除噪声：年份、纯序号
def extract_numbers(text: str) -> set:
    out = set()
    for m in NUM_RE.finditer(text or ""):
        v = m.group()
        if re.fullmatch(r"20\d{2}", v):      # 年份
            continue
        try:
            if float(v) < 1:
                continue
        except ValueError:
            continue
        out.add(v)
    return out


def resolve_cites(text: str, corpus_keys) -> list:
    """把答案里的《X》解析成语料文件名（子串匹配）。"""
    out = []
    for m in CITE_RE.finditer(text or ""):
        cn = norm(m.group(1))
        if len(cn) < 3:
            continue
        for k in corpus_keys:
            kn = norm(k)
            if cn in kn or kn in cn:
                out.append(k)
                break
    return out


def retrieved_text(row: dict, corpus: dict, include_cited: bool = True) -> str:
    """拼出近似"模型看到的上下文"。

    局限：结果文件只记了 top-10 文件名（run_eval 里 search_files(top_k=10)），
    而模型实际看到 K=20 个 chunk。因此额外把答案引用到的文档正文补进来，
    减少"引用到 top-10 之外文档 → 被误判无据"的假阳性。
    """
    names = list(row.get("retrievedFiles") or [])
    if include_cited:
        for k in resolve_cites(row.get("answer"), list(corpus.keys())):
            if k not in names:
                names.append(k)
    parts = []
    for name in names:
        t = corpus.get(name)
        if t:
            parts.append(t)
    return "\n".join(parts)


def deterministic_metrics(row: dict, corpus: dict) -> dict:
    ans_raw = row.get("answer") or ""
    # 接地检查前先剔除《文件名》引用与【标签】：它们的数字来自文件名/元数据，不在 chunk 正文里，
    # 否则会把"《01-年假管理制度》"里的 01 误判为无据数字（上下文标注上线后出现过这个假象）
    ans = re.sub(r"《[^》]*》", "", ans_raw)
    ans = re.sub(r"【[^】]*】", "", ans)
    ctx = retrieved_text(row, corpus)
    ctx_n = norm(ctx)
    ans_nums = extract_numbers(ans)
    grounded = {n for n in ans_nums if n in ctx_n}
    ungrounded = sorted(ans_nums - grounded)

    # 引用有效性：三级判定
    #   in_retrieved  —— 在记录的检索文件里（最可信）
    #   in_corpus     —— 语料存在但不在记录的 top-10 里（测量局限：上下文只有 top-10 文件名）
    #   not_found     —— 语料里根本没有这个名字（真幻觉信号）
    cites = set()
    for m in CITE_RE.finditer(ans_raw):
        cites.add(m.group(1))
    retrieved = row.get("retrievedFiles") or []
    corpus_keys = list(corpus.keys())

    def strip_noise(x: str) -> str:
        """去掉文件名前导编号（如 10-专项假期管理规定 → 专项假期管理规定）与括号补充。"""
        x = re.sub(r"^\d+[-_]", "", norm(x))
        x = re.sub(r"（[^）]*）|\([^)]*\)", "", x)
        return x

    def match_any(c: str, names) -> bool:
        cn = strip_noise(c)
        if len(cn) < 3:
            return False
        for r in names:
            rn = strip_noise(r)
            if cn in rn or rn in cn:
                return True
        return False

    # 《》既可指文档、也可指表单/制度名——若该名称出现在语料正文里，不算幻觉引用
    corpus_text_all = norm("\n".join(corpus.values()))
    def appears_in_corpus_text(c: str) -> bool:
        cn = strip_noise(c)
        return len(cn) >= 3 and cn in corpus_text_all

    in_retrieved = sorted(c for c in cites if match_any(c, retrieved))
    in_corpus = sorted(c for c in cites
                       if c not in in_retrieved and match_any(c, corpus_keys))
    as_text = sorted(c for c in cites
                     if c not in in_retrieved and c not in in_corpus
                     and appears_in_corpus_text(c))
    not_found = sorted(c for c in cites
                       if c not in in_retrieved and c not in in_corpus and c not in as_text)
    valid_cites, invalid_cites = in_retrieved, not_found

    expected = row.get("factsExpected") or []
    hits = row.get("factHits") or []
    recall = (len(hits) / len(expected)) if expected else None

    return {
        "factRecall": recall,
        "numbersTotal": len(ans_nums),
        "numbersGrounded": len(grounded),
        "groundingRate": (len(grounded) / len(ans_nums)) if ans_nums else None,
        "ungroundedNumbers": ungrounded,
        "citationsTotal": len(cites),
        "validCitations": valid_cites,
        "invalidCitations": invalid_cites,
        "citationsInCorpusNotInRecorded": in_corpus,
        "citationsAsFormOrTermName": as_text,
        "contextChars": len(ctx),
    }


# ---------- judge ----------

JUDGE_PROMPT = """你是严格的 RAG 答案评审。请根据【问题】【期望事实】【检索到的文档内容】【待评答案】给出三项评分。

评分标准（每项 0-3 分）：
- correctness（正确性）：答案的事实是否与【期望事实】一致、无错误。
  3=全部正确且覆盖期望事实；2=覆盖大部分但有缺漏或小错；1=方向对但有实质错误；0=错误或无关。
- faithfulness（忠实度）：答案中的每条论断是否都能被【检索到的文档内容】支撑。
  3=全部有据；2=有少量合理推断但无编造；1=存在明显无据论断；0=大面积编造。
- relevance（相关性）：答案是否正面回答了【问题】。
  3=直接回答；2=基本回答但有偏移/冗余；1=部分答非所问；0=答非所问。

只输出 JSON，不要解释：
{"correctness": 0-3, "faithfulness": 0-3, "relevance": 0-3,
 "unsupportedClaims": ["答案中无据的论断，逐条列出，最多3条"], "note": "一句话理由"}"""


def call_judge(row: dict, corpus: dict, model: str, api_key: str, retries: int = 2) -> dict:
    ctx = retrieved_text(row, corpus)[:12000]
    expected = row.get("factsExpected") or []
    user = (
        f"【问题】{row.get('question')}\n\n"
        f"【期望事实】{', '.join(expected) if expected else '（无，属于拒答/开放类）'}\n"
        f"【可接受替代】{', '.join(row.get('alternateFacts') or []) or '（无）'}"
        f"（仅当答案明确指出冲突并说明采信依据时，满足替代项也算正确）\n\n"
        f"【检索到的文档内容】\n{ctx}\n\n"
        f"【待评答案】\n{(row.get('answer') or '')[:4000]}"
    )
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": JUDGE_PROMPT},
                     {"role": "user", "content": user}],
        "temperature": 0,
    }, ensure_ascii=False).encode("utf-8")

    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(DASH_BASE, data=body, headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            })
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            text = data["choices"][0]["message"]["content"]
            m = re.search(r"\{.*\}", text, re.S)
            obj = json.loads(m.group()) if m else {}
            return {
                "correctness": obj.get("correctness"),
                "faithfulness": obj.get("faithfulness"),
                "relevance": obj.get("relevance"),
                "unsupportedClaims": obj.get("unsupportedClaims") or [],
                "note": obj.get("note", ""),
            }
        except Exception as e:  # noqa: BLE001
            last = str(e)
            time.sleep(1.5 * (attempt + 1))
    return {"error": last}


# ---------- 主流程 ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True, help="run_eval 产出的结果 JSON")
    ap.add_argument("--judge", action="store_true", help="启用 LLM judge（需要 ALIYUN_API_KEY）")
    ap.add_argument("--model", default="qwen-plus")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--label", default="")
    args = ap.parse_args()

    src = Path(args.results)
    if not src.is_absolute():
        src = (Path.cwd() / src) if (Path.cwd() / src).exists() else (HERE / src)
    data = json.loads(src.read_text(encoding="utf-8"))
    rows = data.get("rows") or []
    if args.limit:
        rows = rows[: args.limit]

    corpus = load_corpus()
    api_key = os.environ.get("ALIYUN_API_KEY", "")
    if args.judge and not api_key:
        print("!! 未设置 ALIYUN_API_KEY，跳过 judge", file=sys.stderr)
        args.judge = False

    out_rows = []
    for i, r in enumerate(rows, 1):
        m = deterministic_metrics(r, corpus)
        rec = {"id": r.get("id"), "category": r.get("category"), **m}
        if args.judge:
            j = call_judge(r, corpus, args.model, api_key)
            rec.update({f"judge_{k}": v for k, v in j.items()})
            print(f"[{i}/{len(rows)}] {rec['id']}  "
                  f"correct={j.get('correctness')} faithful={j.get('faithfulness')} "
                  f"relevant={j.get('relevance')}", flush=True)
        else:
            print(f"[{i}/{len(rows)}] {rec['id']}  grounding={m['groundingRate']}", flush=True)
        out_rows.append(rec)

    # 汇总
    def avg(key):
        vals = [x[key] for x in out_rows if isinstance(x.get(key), (int, float))]
        return round(sum(vals) / len(vals), 3) if vals else None

    summary = {
        "source": src.name,
        "generatedAt": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "questions": len(out_rows),
        "judgeModel": args.model if args.judge else None,
        # 确定性
        "avgFactRecall": avg("factRecall"),
        "avgGroundingRate": avg("groundingRate"),
        "questionsWithUngroundedNumbers": sum(1 for x in out_rows if x["ungroundedNumbers"]),
        "questionsWithInvalidCitations": sum(1 for x in out_rows if x["invalidCitations"]),
        "questionsWithCitationsOutsideRecorded": sum(
            1 for x in out_rows if x["citationsInCorpusNotInRecorded"]),
        "questionsWithFormNameCitations": sum(
            1 for x in out_rows if x["citationsAsFormOrTermName"]),
        # judge
        "avgCorrectness": avg("judge_correctness"),
        "avgFaithfulness": avg("judge_faithfulness"),
        "avgRelevance": avg("judge_relevance"),
        "questionsWithUnsupportedClaims": sum(
            1 for x in out_rows if x.get("judge_unsupportedClaims")),
    }

    label = args.label or src.stem
    out = RESULTS / f"gen-eval-{label}-{summary['generatedAt']}.json"
    out.write_text(json.dumps({"summary": summary, "rows": out_rows}, ensure_ascii=False, indent=2),
                   encoding="utf-8")

    print("\n===== 汇总 =====")
    for k, v in summary.items():
        print(f"  {k:34s} = {v}")
    print(f"\n结果写入: {out}")

    # markdown 报告
    md = RESULTS / f"gen-eval-{label}-{summary['generatedAt']}.md"
    lines = [f"# 生成层评估报告（{label}）", "",
             f"- 来源: `{src.name}`，题目数 **{summary['questions']}**",
             f"- judge 模型: {summary['judgeModel'] or '（未启用，仅确定性指标）'}", "",
             "## 汇总", "", "| 指标 | 值 |", "|---|---|"]
    for k, v in summary.items():
        if k in ("source", "generatedAt"):
            continue
        lines.append(f"| {k} | {v} |")
    lines += ["", "## 逐题", "",
              "| 题 | 类别 | 事实召回 | 数字接地率 | 无据数字 | 幻觉引用 | 引用超记录 | judge 正确/忠实/相关 |",
              "|---|---|---|---|---|---|---|---|"]
    for x in out_rows:
        lines.append("| {id} | {cat} | {rec} | {gr} | {un} | {ic} | {oc} | {c}/{f}/{r} |".format(
            id=x["id"], cat=x.get("category", ""),
            rec=f"{x['factRecall']:.2f}" if isinstance(x["factRecall"], float) else "-",
            gr=f"{x['groundingRate']:.2f}" if isinstance(x["groundingRate"], float) else "-",
            un=", ".join(x["ungroundedNumbers"]) or "-",
            ic=", ".join(x["invalidCitations"]) or "-",
            oc=", ".join(x["citationsInCorpusNotInRecorded"]) or "-",
            c=x.get("judge_correctness", "-"), f=x.get("judge_faithfulness", "-"),
            r=x.get("judge_relevance", "-")))
    md.write_text("\n".join(lines), encoding="utf-8")
    print(f"报告写入: {md}")


if __name__ == "__main__":
    main()
