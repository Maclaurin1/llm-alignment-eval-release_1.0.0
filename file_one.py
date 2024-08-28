# coding: utf-8
# @author: kaimin
# @time: 2024-06-17 13:57
import json
import os

import numpy as np
from tqdm import tqdm

from transformers import AutoTokenizer


def split_response_tokens(p_tokens):
    # 创建一个长度为3的滑动窗口，用于匹配连续出现的三个数字
    window = np.lib.stride_tricks.sliding_window_view(p_tokens, window_shape=(3,))

    # 找到连续出现的匹配位置
    matches = np.where(np.all(window == [151644, 120458, 22564], axis=1))[0]

    # 如果有匹配的位置，则截取最后一次匹配到的位置之后的数据
    if len(matches) > 0:
        last_match = matches[-1]
        result = p_tokens[last_match + 3:]
        return result.tolist()
    else:
        return []



src_path = r"D:\eval\llm-alignment-eval-release_1.0.0\llm-alignment-eval-release_1.0.0\eval_data\alignment_eval_with_summary_240704_11661_str_consis_hyper_parameters.json"
target_path = r"D:\eval\llm-alignment-eval-release_1.0.0\llm-alignment-eval-release_1.0.0\output\zhaowen_32k_0823"

dc_results_path = target_path


token_path = r"D:\eval\llm-alignment-eval-release_1.0.0\llm-alignment-eval-release_1.0.0\tokenizer\qwen_shuffle_tokenizer"

org_data_map = dict()

fr = open(src_path, mode="r", encoding="utf-8")
org_data = json.load(fr)
fr.close()
# fr = open("./data/busEval_769_with_ref_answer_zh_prompt.json", mode="r", encoding="utf-8")
# org_data += json.load(fr)
# fr.close()
# fr = open("./data/mx_uq_240612_with_info_1282.json", mode="r", encoding="utf-8")
# org_data += json.load(fr)
# fr.close()

for td in org_data:
    org_data_map[td['trace_id']] = td

json_files = []
for root, dirs, files in os.walk(target_path):
    for file in files:
        print(file)
        if file.endswith('.jsonl'):
            json_files.append(os.path.join(root, file))
json_files = sorted(json_files)
print(json_files)
tkn = AutoTokenizer.from_pretrained(token_path)

for tf in json_files:
    fr = open(tf, mode="r", encoding='utf-8')
    lines = fr.readlines()
    fr.close()
    data_list = []

    for tl in tqdm(lines):
        td = json.loads(tl)
        t_id = td['trace_id']

        tokens = td['outputs']

        # response_tokens = split_response_tokens(tokens)
        response_tokens = tokens
        if len(response_tokens) > 0:
            response = tkn.decode(response_tokens)
        else:
            response = ""

        if t_id in org_data_map:
            md = org_data_map.get(t_id).copy()
            md['response'] = response

            data_list.append(md)

    parent_dir = os.path.dirname(tf)
    parent_dir_name = os.path.basename(parent_dir)
    # dc_dir = os.path.join(dc_results_path, parent_dir_name)
    # os.makedirs(dc_dir, exist_ok=True)
    results_file = os.path.join(dc_results_path, f"{parent_dir_name}_results.jsonl")

    fw = open(results_file, mode="w", encoding="utf-8")
    print(results_file)
    for td in data_list:
        fw.write(json.dumps(td, ensure_ascii=False) + "\n")
    fw.close()