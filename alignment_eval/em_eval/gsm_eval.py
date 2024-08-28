# coding: utf-8
# @author: kaimin
# @time: 2024-05-13 17:37
import json
from typing import List, Dict
from .base_eval import BaseEval


class GsmEval(BaseEval):
    def __init__(self):
        super().__init__()

    @staticmethod
    def _gpt_score(p_sample: Dict):
        t_ref = p_sample['reference'].split("\n#### ")
        t_ref = t_ref[-1]

        if f"the answer is {t_ref}" in p_sample['response'].lower() or f"the answer is ${t_ref}" in p_sample['response'].lower():
            return 1
        else:
            return 0

    def score(self, p_samples: List[Dict], p_res_path: str):
        score_list = []

        for ts in p_samples:
            t_score = self._gpt_score(ts)
            ts['score'] = t_score
            score_list.append(t_score)

        fw = open(p_res_path, mode="w", encoding="utf-8")
        json.dump(p_samples, fw, ensure_ascii=False, indent=2)
        fw.close()

        print(f"res path {p_res_path}, score: {sum(score_list) / len(score_list)}")
        return {"score": sum(score_list) / len(score_list) * 100}
