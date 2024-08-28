# coding: utf-8
# @author: kaimin
# @time: 2024-04-02 19:02
import json
from typing import List, Dict

from .base_eval import BaseEval
from .ZhIFEval.evaluation_main import (InputExample, test_instruction_following_loose,
                                       test_instruction_following_strict)


class ZhIFEval(BaseEval):
    def __init__(self):
        super().__init__()

    def score(self, p_samples: List[Dict], p_res_path: str):
        results = dict()
        for metric in ('if_strict', 'if_loose'):
            results[metric] = []

        for t_smp in p_samples:
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
            t_smp['score'] = t_smp['if_strict']

        final_scores = dict()

        for metric in ('if_strict', 'if_loose'):
            prompt_total = 0
            prompt_correct = 0
            inst_total = 0
            inst_correct = 0

            for example in results[metric]:
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

        fw = open(p_res_path, mode="w", encoding="utf-8")
        json.dump(p_samples, fw, ensure_ascii=False, indent=2)
        fw.close()

        final_scores['score'] = (final_scores['Prompt-level-if_loose-accuracy'] + final_scores['Inst-level-if_strict-accuracy']) / 2
        print(f"res path {p_res_path}, score {json.dumps(final_scores)}")
        return final_scores