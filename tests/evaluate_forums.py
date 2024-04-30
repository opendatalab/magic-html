# -*- coding: utf-8 -*-
import logging

logging.basicConfig(level=logging.INFO)

import json
import jieba

jieba.setLogLevel(logging.INFO)
from tabulate import tabulate
import numpy as np

from copy import deepcopy
from bs4 import BeautifulSoup
from ltp import StnSplit
from rouge_score.rouge_scorer import _summary_level_lcs

stp = StnSplit()


def get_score(target, prediction):
    def get_sents(text):
        # 分句
        sents = stp.split(text)
        sents = [x for x in sents if len(x)]
        return sents

    target_tokens_list = [
        [x for x in jieba.lcut(s) if x != " "] for s in get_sents(target)
    ]
    prediction_tokens_list = [
        [x for x in jieba.lcut(s) if x != " "] for s in get_sents(prediction)
    ]

    scoress = _summary_level_lcs(target_tokens_list, prediction_tokens_list)
    return scoress


def rouge_eval(ref, cand):
    """
    计算给定的参考文本和候选文本之间的rouge-L的precision，recall and F1 score
    :param ref: str, reference_txt， 即true label
    :param cand: str, candidate_text， 即pred label
    :return: 列表，元素是字典
    """
    t = {"prec": 1, "rec": 1, "f1": 1}
    if ref == cand:
        return t
    score = get_score(ref, cand)
    t["prec"] = score.precision
    t["rec"] = score.recall
    t["f1"] = score.fmeasure
    return t


def evaluate_result(datas):
    scores = []
    prec = []
    rec = []
    for x in datas:
        scores.append(rouge_eval(x["content"], x["extract_content"]))
    for item in scores:
        prec.append(item["prec"])
        rec.append(item["rec"])

    prec_mean = np.array(prec).mean()
    rec_mean = np.array(rec).mean()
    f1_mean = 2 * prec_mean * rec_mean / (prec_mean + rec_mean)
    global_info["prec_mean"].append(prec_mean)
    global_info["rec_mean"].append(rec_mean)
    global_info["f1_mean"].append(f1_mean)


def get_content_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    # 使用get_text()方法抽取所有文本内容，参数"\n"作为不同标签间的分隔符，strip=True去除多余空白
    text_content = soup.get_text("\n", strip=True)
    return text_content


global_datas = []

global_info = {
    "func": [],
    "prec_mean": [],
    "rec_mean": [],
    "f1_mean": [],
}

with open("data/forum/base.json", "r", encoding="utf-8") as f:
    for k, v in json.loads(f.read()).items():
        html_str = ""
        with open(f"data/forum/htmls/{k}.html", "r", encoding="utf-8") as ff:
            html_str = ff.read()
            v["html"] = html_str
        global_datas.append(v)


def run_common_html_extractor(name):
    from common_html_extractor import GeneralExtractor

    datas = deepcopy(global_datas)
    extractor = GeneralExtractor()
    for x in datas:
        x["extract_content"] = get_content_text(
            extractor.extract(html=x["html"], base_url=x["url"], html_type="forum")[
                "html"
            ]
        )
    global_info["func"].append(name)
    evaluate_result(datas)


def run_trafilatura(name):
    from trafilatura import extract

    datas = deepcopy(global_datas)
    for x in datas:
        x["extract_content"] = extract(
            x["html"], include_comments=True, no_fallback=True
        )
    global_info["func"].append(name)
    evaluate_result(datas)


def run_trafilatura_fallback(name):
    from trafilatura import extract

    datas = deepcopy(global_datas)
    for x in datas:
        x["extract_content"] = extract(
            x["html"], include_comments=True, no_fallback=False
        )
    global_info["func"].append(name)
    evaluate_result(datas)


# 自定义需要对比的方法
all_funcs = {
    "common_html_extractor": run_common_html_extractor,
    "trafilatura": run_trafilatura,
    "trafilatura_fallback": run_trafilatura_fallback,
}

for k, v in all_funcs.items():
    v(k)

print("论坛类型网页")
print("当前结果")
print(tabulate(global_info, headers="keys", tablefmt="fancy_grid"))
print("基准结果")
print('''
╒═══════════════════════╤═════════════╤════════════╤═══════════╕
│ func                  │   prec_mean │   rec_mean │   f1_mean │
╞═══════════════════════╪═════════════╪════════════╪═══════════╡
│ common_html_extractor │    0.752323 │   0.964762 │  0.845401 │
├───────────────────────┼─────────────┼────────────┼───────────┤
│ trafilatura           │    0.711983 │   0.568848 │  0.632418 │
├───────────────────────┼─────────────┼────────────┼───────────┤
│ trafilatura_fallback  │    0.781724 │   0.557774 │  0.651028 │
╘═══════════════════════╧═════════════╧════════════╧═══════════╛
''')
