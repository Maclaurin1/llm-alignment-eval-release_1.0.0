# coding: utf-8
# @author: kaimin
# @time: 2024-05-13 17:52

import json
import re
from typing import List, Dict
from alignment_eval.em_eval.base_eval import BaseEval



def extract_length_depth(s):
    # 使用正则表达式提取Length和Depth的数值
    match = re.search(r'Length(\d+)Depth([\d\.]+)', s)
    if match:
        length = int(match.group(1))  # 提取Length的值
        depth = float(match.group(2))  # 提取Depth的值
        return (length, depth)
    else:
        return (0, 0)  # 如果没有匹配到，返回默认值


class ExactMatchEval(BaseEval):
    def __init__(self):
        super().__init__()

    @staticmethod
    def text_match(p_sample: Dict):
        s1 = p_sample['reference'].strip()
        s2 = p_sample['response'].strip()

        if s1 == s2:
            return 1.0
        else:
            return 0.0

    def score(self, p_samples: List[Dict], p_res_path: str):
        score_list = []
        score_map = {}

        for ts in p_samples:
            t_score = self.text_match(ts)
            ts['score'] = t_score
            score_list.append(t_score)

            map_key = ts['trace_id'][0: ts['trace_id'].rindex("_")]
            if map_key not in score_map:
                score_map[map_key] = []

            score_map[map_key].append(t_score)

        fw = open(p_res_path + ".json", mode="w", encoding="utf-8")
        json.dump(p_samples, fw, ensure_ascii=False, indent=2)
        fw.close()

        ret_score_map = {}

        fw = open(p_res_path + ".csv", mode="w", encoding="utf-8")
        sorted_data = dict(sorted(score_map.items(), key=lambda item: extract_length_depth(item[0])))
        fw.write("dataset,model\n")
        for k, v in sorted_data.items():
            fw.write(f"{k},{sum(v) / len(v) * 100}\n")
            ret_score_map[k] = sum(v) / len(v) * 100
        fw.close()

        """
        dataset,chatglm2-6b
        CDME_Length1000Depth0,55.87
        CDME_Length1000Depth5,43.97
        CDME_Length1000Depth10,35.61
        """

        print(f"res path {p_res_path}, score {sum(score_list) / len(score_list)}")
        ret_score_map["score"] = sum(score_list) / len(score_list) * 100

        return ret_score_map
