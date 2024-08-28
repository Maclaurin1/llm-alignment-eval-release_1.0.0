# coding: utf-8
# @author: kaimin
# @time: 2024-04-17 16:32
import json

import jieba

from typing import List, Dict

from .base_eval import BaseEval
from .ZhIFEval.evaluation_main import (InputExample, test_instruction_following_loose,
                                       test_instruction_following_strict)


class RAIFBEval(BaseEval):
    def __init__(self, p_mx_model=False):
        super().__init__()
        self.mx_model = p_mx_model

    def _rouge_l(self, p_key, p_response):
        """
        计算中文 rouge l 分数，使用结巴分词，词维度计算

        :param p_key:
        :param p_response:
        :return:
        """

        if self.mx_model:
            p_key = p_key.replace("，", ",")
            p_response = p_response.replace("，", ",")

        key_words = jieba.lcut(p_key)
        response_words = jieba.lcut(p_response)

        key_len = len(key_words)
        response_len = len(response_words)

        if key_len == 0 or response_len == 0:
            return 0.0

        lcs = [[0] * (response_len + 1) for _ in range(key_len + 1)]

        for i in range(1, key_len + 1):
            for j in range(1, response_len + 1):
                if key_words[i - 1] == response_words[j - 1]:
                    lcs[i][j] = lcs[i - 1][j - 1] + 1
                else:
                    lcs[i][j] = max(lcs[i - 1][j], lcs[i][j - 1])

        return lcs[key_len][response_len] / key_len

    @staticmethod
    def _score_if(p_samples: List[Dict]):
        results = dict()
        for metric in ('if_strict', 'if_loose'):
            results[metric] = []

        for t_smp in p_samples:
            if len(t_smp['reference']) == 0 or "信息不足无法回答" in t_smp['response']:
                t_smp['if_strict'] = -1
                t_smp['if_loose'] = -1
                continue

            t_input = InputExample(
                key=t_smp['trace_id'],
                instruction_id_list=t_smp['instruction_id_list'],
                prompt=t_smp['messages'][0]['content'],
                kwargs=t_smp['kwargs']
            )

            for kwarg in t_input.kwargs:
                for k in list(kwarg.keys()):
                    if kwarg[k] is None:
                        kwarg.pop(k, None)

            if_strict = test_instruction_following_strict(t_input, t_smp['response'])
            if_loose = test_instruction_following_loose(t_input, t_smp['response'])
            results['if_strict'].append(if_strict)
            results['if_loose'].append(if_loose)

            t_smp['if_strict'] = sum(if_strict.follow_instruction_list) / len(if_strict.instruction_id_list)
            t_smp['if_loose'] = sum(if_loose.follow_instruction_list) / len(if_loose.instruction_id_list)

        return results

    def _score_rag(self, p_samples: List[Dict]):
        def _strict_check(p_sample: Dict):
            r_keys = p_sample['reference']
            if len(r_keys) == 0:
                if "信息不足无法回答" in p_sample['response']:
                    return 1
                else:
                    return 0
            else:
                correct = 0
                response = p_sample['response']
                if self.mx_model:
                    response = response.replace("，", ",")

                for trk in r_keys:
                    if self.mx_model:
                        trk = trk.replace("，", ",")
                    if trk in response:
                        correct += 1
                return correct / len(r_keys)

        def _loose_check(p_sample: Dict):
            r_keys = p_sample['reference']
            if len(r_keys) == 0:
                if "无法回答" in p_sample['response'] or "信息不足" in p_sample['response']:
                    return 1
                else:
                    return 0
            else:
                correct = 0
                for trk in r_keys:
                    correct += self._rouge_l(trk, p_sample['response'])
                return correct / len(r_keys)

        results = dict()
        for metric in ('rag_strict', 'rag_loose'):
            results[metric] = []

        for t_smp in p_samples:
            strict_score = _strict_check(t_smp)
            loose_score = _loose_check(t_smp)
            results['rag_strict'].append(strict_score)
            results['rag_loose'].append(loose_score)

            t_smp['rag_strict'] = strict_score
            t_smp['rag_loose'] = loose_score

            t_smp['score'] = (t_smp['if_loose'] + t_smp['rag_loose']) / 2

        return results

    def score(self, p_samples: List[Dict], p_res_path: str):
        if_score_details = self._score_if(p_samples)
        rag_score_details = self._score_rag(p_samples)
        final_scores = {}

        fw = open(p_res_path, mode="w", encoding="utf-8")
        json.dump(p_samples, fw, ensure_ascii=False, indent=2)
        fw.close()

        for metric in ('if_strict', 'if_loose'):
            prompt_total = 0
            prompt_correct = 0
            inst_total = 0
            inst_correct = 0

            for example in if_score_details[metric]:
                follow_instruction_list = example.follow_instruction_list
                instruction_id_list = example.instruction_id_list

                prompt_total += 1
                if all(follow_instruction_list):
                    prompt_correct += 1

                inst_total += len(instruction_id_list)
                inst_correct += sum(follow_instruction_list)
            prompt_score = f'Prompt-level-{metric}-accuracy'
            inst_score = f'Inst-level-{metric}-accuracy'
            final_scores[prompt_score] = prompt_correct / prompt_total * 100
            final_scores[inst_score] = inst_correct / inst_total * 100

        for metric in ('rag_strict', 'rag_loose'):
            final_scores[metric] = sum(rag_score_details[metric]) / len(rag_score_details[metric]) * 100

        final_scores['score'] = (final_scores['Prompt-level-if_loose-accuracy'] + final_scores['rag_loose']) / 2
        print(f"res path {p_res_path}, score {json.dumps(final_scores)}")

        return final_scores
