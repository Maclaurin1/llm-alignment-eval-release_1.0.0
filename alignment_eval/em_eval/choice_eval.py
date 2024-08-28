# coding: utf-8
# @author: kaimin
# @time: 2024-04-01 11:19
import json
from typing import List, Dict

from .base_eval import BaseEval


class ChoiceEval(BaseEval):
    def __init__(self):
        super().__init__()

    @staticmethod
    def check_choice(p_options, p_reference, p_response):
        for tc in p_response:
            if tc in p_options:
                if tc == p_reference:
                    return 1
                else:
                    return 0
        return 0

    def score(self, p_samples: List[Dict], p_res_path: str):
        score_list_map = {}
        score_map = {}

        for t_smp in p_samples:
            t_res = self.check_choice(t_smp['options'], t_smp['reference'], t_smp['response'])
            t_smp['score'] = t_res
            if t_smp['category'] not in score_list_map:
                score_list_map[t_smp['category']] = []
            score_list_map[t_smp['category']].append(t_res)

        fw = open(p_res_path, mode="w", encoding="utf-8")
        json.dump(p_samples, fw, ensure_ascii=False, indent=2)
        fw.close()

        scores = 0

        for k, v in score_list_map.items():
            score_map[k] = sum(v) / len(v) * 100
            scores += sum(v) / len(v) * 100
        score_map['score'] = scores / len(score_list_map)

        return score_map
