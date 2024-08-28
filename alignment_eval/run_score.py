# coding: utf-8
# @author: kaimin
# @time: 2024-05-14 13:07
import argparse
import json
import os.path
import nltk
nltk.download('punkt')

import pandas as pd
from alignment_eval.em_eval import *
from alignment_eval.utils.cdme_pic_utils import visualize

score_map = {}


def to_alignbench_csv(p_samples, p_res_path):
    answers = []
    for ts in p_samples:
        answers.append(ts['response'])

    df = pd.DataFrame(answers, columns=['answers'])
    df.to_csv(p_res_path, index=False)

    # remove header 'answer'
    fr = open(p_res_path, mode="r", encoding="utf-8")
    lines = fr.readlines()
    fr.close()

    fw = open(p_res_path, mode="w", encoding="utf-8")
    for tl in lines[1:]:
        fw.write(tl)
    fw.close()


def raifb_sp_score(p_samples, p_res_path):
    global score_map

    api_1_list = []
    api_2_list = []

    for ts in p_samples:
        if ts['subcategory'] == "system_inst_add":
            api_1_list.append(ts)
        elif ts['subcategory'] == "message_inst_add":
            api_2_list.append(ts)

    m_eval = RAIFBEval(p_mx_model=True)
    part_1 = []
    part_2 = []
    part_3 = []
    for ts in api_1_list:
        if ts['category'] == 'part1':
            part_1.append(ts)
        elif ts['category'] == 'part2':
            part_2.append(ts)
        elif ts['category'] == 'part3':
            part_3.append(ts)
    if len(part_1) > 0:
        t_res = m_eval.score(part_1, f"{p_res_path}_api1_part1.json")
        score_map['RAIFB_api1_part1'] = t_res
    if len(part_2) > 0:
        t_res = m_eval.score(part_2, f"{p_res_path}_api1_part2.json")
        score_map['RAIFB_api1_part2'] = t_res
    if len(part_3) > 0:
        t_res = m_eval.score(part_3, f"{p_res_path}_api1_part3.json")
        score_map['RAIFB_api1_part3'] = t_res

    part_1 = []
    part_2 = []
    part_3 = []
    for ts in api_2_list:
        if ts['category'] == 'part1':
            part_1.append(ts)
        elif ts['category'] == 'part2':
            part_2.append(ts)
        elif ts['category'] == 'part3':
            part_3.append(ts)
    if len(part_1) > 0:
        t_res = m_eval.score(part_1, f"{p_res_path}_api2_part1.json")
        score_map['RAIFB_api2_part1'] = t_res
    if len(part_2) > 0:
        t_res = m_eval.score(part_2, f"{p_res_path}_api2_part2.json")
        score_map['RAIFB_api2_part2'] = t_res
    if len(part_3) > 0:
        t_res = m_eval.score(part_3, f"{p_res_path}_api2_part3.json")
        score_map['RAIFB_api2_part3'] = t_res


def do_score(p_data_path, p_out_dir, p_model_name):
    global score_map

    to_eval_data_map = {}
    fr = open(p_data_path, mode="r", encoding="utf-8")
    lines = fr.readlines()
    fr.close()

    for tl in lines:
        td = json.loads(tl)
        if 'eval_set_name' not in td:
            continue
        if td['eval_set_name'] not in to_eval_data_map:
            to_eval_data_map[td['eval_set_name']] = []
        to_eval_data_map[td['eval_set_name']].append(td)

    for k, v in to_eval_data_map.items():
        res_path = os.path.join(p_out_dir, f"{p_model_name}_{k}")
        if k in ["CDME", "CDME_NF"]:
            m_eval = EdEval()
            t_res = m_eval.score(v, res_path)
            score_map[k] = t_res
            visualize(res_path + ".csv", "32K", p_model_name)
        elif k in ["MT_Eval_C"]:
            m_eval = ExactMatchEval()
            t_res = m_eval.score(v, res_path)
            score_map[k] = t_res
            visualize(res_path + ".csv", "32K", p_model_name)
        elif k in ["ceval", "emfin", "mmlu", "abcEval"]:
            m_eval = ChoiceEval()
            res_path += ".json"
            t_res = m_eval.score(v, res_path)
            score_map[k] = t_res
        elif k in ["IFEval"]:
            m_eval = IFEval()
            res_path += ".json"
            t_res = m_eval.score(v, res_path)
            score_map[k] = t_res
        elif k in ["ZhIFEval"]:
            m_eval = ZhIFEval()
            res_path += ".json"
            t_res = m_eval.score(v, res_path)
            score_map[k] = t_res
        elif k in ["RAIFB"]:
            raifb_sp_score(v, res_path)
        elif k in ["gsm"]:
            m_eval = GsmEval()
            res_path += ".json"
            t_res = m_eval.score(v, res_path)
            score_map[k] = t_res
        elif k in ["AlignBench"]:
            res_path += ".csv"
            to_alignbench_csv(v, res_path)

    score_map = dict(sorted(score_map.items(), key=lambda x: x[0]))
    fw = open(os.path.join(p_out_dir, "scores_sum.json"), mode="w", encoding="utf-8")
    json.dump(score_map, fw, ensure_ascii=False, indent=2)
    fw.close()

DF_MODEL_NAME = "zhaowen_32k_0823"
DF_RES_PATH = f"D:/eval/llm-alignment-eval-release_1.0.0/llm-alignment-eval-release_1.0.0/output/{DF_MODEL_NAME}/{DF_MODEL_NAME}_results.jsonl"
DF_OUT_DIR = f"D:/eval/llm-alignment-eval-release_1.0.0/llm-alignment-eval-release_1.0.0/output/{DF_MODEL_NAME}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", default=DF_RES_PATH, help="数据路径")
    parser.add_argument("--out_dir", default=DF_OUT_DIR, help="输出路径")
    parser.add_argument("--model_name", default=DF_MODEL_NAME, help="模型名")
    args = parser.parse_args()

    do_score(args.data_path, args.out_dir, args.model_name)
    print(f"finish score out dir {args.out_dir}")