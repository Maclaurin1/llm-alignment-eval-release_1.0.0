# coding: utf-8
# @author: kaimin
# @time: 2024-05-13 17:52

import json
import re
from typing import List, Dict
from .base_eval import BaseEval


def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    # 如果其中一个字符串为空，那么只能通过删除另一个字符串中的所有字符来实现
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # 计算最小操作数：插入、删除或替换
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def extract_length_depth(s):
    # 使用正则表达式提取Length和Depth的数值
    match = re.search(r'Length(\d+)Depth([\d\.]+)', s)
    if match:
        length = int(match.group(1))  # 提取Length的值
        depth = float(match.group(2))  # 提取Depth的值
        return (length, depth)
    else:
        return (0, 0)  # 如果没有匹配到，返回默认值


class EdEval(BaseEval):
    def __init__(self):
        super().__init__()

    @staticmethod
    def text_similarity(p_sample: Dict):
        s1 = p_sample['reference'].strip()
        s2 = p_sample['response'].strip()

        # 计算编辑距离
        distance = levenshtein_distance(s1, s2)

        # 计算两个文本长度的总和
        check_length = len(s1)

        # 避免除以零
        if check_length == 0:
            return 1.0

        if check_length - distance < 0:
            return 0
        # 计算相似度值，归一化到 [0, 1] 范围内
        similarity = (check_length - distance) / check_length

        return similarity

    def score(self, p_samples: List[Dict], p_res_path: str):
        score_list = []
        score_map = {}

        for ts in p_samples:
            t_score = self.text_similarity(ts)
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
