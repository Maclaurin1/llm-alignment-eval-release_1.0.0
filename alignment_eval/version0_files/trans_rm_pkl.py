# coding: utf-8
# @author: kaimin
# @time: 2024-01-31 16:27
import argparse
import json
import pickle

from transformers import AutoTokenizer

from alignment_eval.utils.mx_generation_utils import build_inputs, build_result


def trans_rm_pkl(p_data_path, p_results_path, p_tokenizer_path, p_add_system=True):
    def _build_messages(p_messages):
        ret_messages = list()
        for tm in p_messages:
            ret_messages.append((tm['role'], tm['content']))
        return ret_messages

    with open(p_data_path, 'r', encoding="utf-8") as file:
        data = file.readlines()

    tokenizer = AutoTokenizer.from_pretrained(p_tokenizer_path, use_fast=False, trust_remote_code=True)

    data_list = list()
    for tl in data:
        td = json.loads(tl)
        t_msg = _build_messages(td['messages'])
        if p_add_system:
            query = build_inputs(t_msg, tokenizer, td['system_content'])
        else:
            query = build_inputs(t_msg, tokenizer)
        response = build_result(td['response'], tokenizer)
        md = {
            "query": query,
            "response": [response],
            "id": td['trace_id']
        }
        data_list.append(md)

    fw = open(p_results_path, mode="wb")
    pickle.dump(data_list, fw)
    fw.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", help="结果文件，jsonl")
    parser.add_argument("--pkl_path", help="输出结果文件，pkl")
    parser.add_argument("--tokenizer", help="tokenizer")
    parser.add_argument("--add_system", action='store_true', help="是否加system")
    args = parser.parse_args()

    trans_rm_pkl(args.data_path, args.pkl_path, args.tokenizer, args.add_system)
    print(f"finish trans to rm pkl {args.pkl_path}")
