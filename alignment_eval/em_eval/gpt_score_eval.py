# coding: utf-8
# @author: kaimin
# @time: 2024-04-01 11:20
import re
import json
import os.path
import uuid
from typing import List, Dict

from tqdm import tqdm
from typing import Union

from .base_eval import BaseEval
from alignment_eval.models import GPTApi, GptIntApi, Conversation


class GPTScoreEval(BaseEval):
    def __init__(self, p_model: Union[GPTApi, GptIntApi]):
        super().__init__()
        self.model = p_model

    def _model_generate(self, p_score_prompt: str):
        prompt_data = {
            "trace_id": str(uuid.uuid4()),
            "system_content": "You are an AI assistant that helps people find information.",
            "messages": [
                {
                    "role": "user",
                    "content": p_score_prompt
                },
            ],
            "top_p": 0.85,
            "top_k": 1,
            "temperature": 0,
            "max_new_tokens": 1000
        }
        data = Conversation(prompt_data)
        return self.model.generate_single(data)

    def _internal_model_generate(self, t_trace_id: str, p_score_prompt: str):
        if not t_trace_id:
            t_trace_id = str(uuid.uuid4())
        prompt_data = {
            "trace_id": t_trace_id,
            "questionText": str([{'user': p_score_prompt}]),
            "type": "gpt-4-turbo",
            "choices": {
                "top_p": 0.85,
                "top_k": 1,
                "temperature": 0,
                "max_new_tokens": 1000
            }
        }
        data = Conversation(prompt_data, gpt_internal_api=True)
        return self.model.generate_single(data)

    def _score_mt_bench(self, p_samples: List[Dict], p_res_path: str):
        def ext_score(p_score_str):
            match = re.search(r'(?<=Rating: \[\[)\d+(?=\]\])', p_score_str)
            if match:
                rating = int(match.group())
            else:
                rating = 1
            return rating

        processed = set()
        scores = {}

        if os.path.exists(p_res_path):
            with open(p_res_path, mode="r", encoding="utf-8") as f:
                lines = f.readlines()
            for tl in lines:
                tr = json.loads(tl)
                processed.add(tr['trace_id'])
                if tr['category'] not in scores:
                    scores[tr['category']] = []
                scores[tr['category']].append(ext_score(tr['gpt_score_result'][0]))
                scores[tr['category']].append(ext_score(tr['gpt_score_result'][1]))

        for t_sample in tqdm(p_samples):
            if t_sample['trace_id'] in processed:
                continue

            t_prompt_1 = t_sample['gpt_score_prompt'][0].replace("{answer}", t_sample['messages'][1]['content'])
            gpt_score_1 = self._model_generate(t_prompt_1)
            t_prompt_2 = t_sample['gpt_score_prompt'][1].replace("{answer_1}", t_sample['messages'][1]['content']).replace("{answer_2}", t_sample['response'])
            gpt_score_2 = self._model_generate(t_prompt_2)
            t_sample['gpt_score_result'] = [gpt_score_1, gpt_score_2]

            score_1 = ext_score(gpt_score_1)
            score_2 = ext_score(gpt_score_2)

            t_sample['score'] = [score_1, score_2]
            if t_sample['category'] not in scores:
                scores[t_sample['category']] = []
            scores[t_sample['category']].append(score_1)
            scores[t_sample['category']].append(score_2)

            fw = open(p_res_path, mode="a", encoding="utf-8")
            fw.write(json.dumps(t_sample, ensure_ascii=False) + "\n")
            fw.close()

        score_list = list()
        ret_score = {}
        for k, v in scores.items():
            print(f"{k}: {sum(v) / len(v)}")
            score_list.append(sum(v) / len(v))
            ret_score[k] = sum(v) / len(v)

        ret_score["score"] = sum(score_list) / len(score_list)
        print(f"总分: {sum(score_list) / len(score_list)}")
        return ret_score

    def _common_gpt_score(self, p_samples: List[Dict], p_res_path: str):
        def ext_score(p_score_str):
            # match = re.search(r'(?<=Rating: \[\[)\d+(?=\]\])', p_score_str)
            match = re.search(r'(?<=评分[:：]\[\[)\d+(?=\]\])', p_score_str)
            match2 = re.search(r'(?<=评分\*\*[:：]\[\[)\d+(?=\]\])', p_score_str)
            match3 = re.search(r'(?<=评分[:：] \[\[)\d+(?=\]\])', p_score_str)
            match4 = re.search(r'(?<=评分\*\*[:：] \[\[)\d+(?=\]\])', p_score_str)
            if match:
                rating = int(match.group())
            elif match2:
                rating = int(match2.group())
            elif match3:
                rating = int(match3.group())
            elif match4:
                rating = int(match4.group())
            else:
                rating = 1
            return rating

        processed = set()
        scores = {}

        if os.path.exists(p_res_path):
            with open(p_res_path, mode="r", encoding="utf-8") as f:
                lines = f.readlines()
            for tl in lines:
                tr = json.loads(tl)
                processed.add(tr['trace_id'])
                if tr['category'] not in scores:
                    scores[tr['category']] = []
                scores[tr['category']].append(ext_score(tr['gpt_score_result'][0]))

        for t_sample in tqdm(p_samples):
            if t_sample['trace_id'] in processed:
                continue

            t_prompt = t_sample['gpt_score_prompt'][0].replace("{answer}", t_sample['response'])
            t_prompt = t_prompt.replace("{ref_answer}", t_sample.get('ref_answer', ''))
            if isinstance(self.model, GptIntApi):
                gpt_score = self._internal_model_generate(t_sample.get('trace_id', ''), t_prompt)
            else:
                gpt_score = self._model_generate(t_prompt)
            t_sample['gpt_score_result'] = [gpt_score]

            score = ext_score(gpt_score)

            t_sample['score'] = [score]
            if t_sample['category'] not in scores:
                scores[t_sample['category']] = []
            scores[t_sample['category']].append(score)

            fw = open(p_res_path, mode="a", encoding="utf-8")
            fw.write(json.dumps(t_sample, ensure_ascii=False) + "\n")
            fw.close()

        score_list = list()
        ret_score = {}
        for k, v in scores.items():
            print(f"{k}: {sum(v) / len(v)}")
            score_list.append(sum(v) / len(v))
            ret_score[k] = sum(v) / len(v)

        ret_score["score"] = sum(score_list) / len(score_list)
        print(f"总分: {sum(score_list) / len(score_list)}")
        return ret_score
    def _score_MT_eval(self, p_samples: List[Dict], p_res_path: str):
        def ext_score(p_score_str):
            # match = re.search(r'(?<=Rating: \[\[)\d+(?=\]\])', p_score_str)
            match = re.search(r'(?<=评分[:：]\[\[)\d+(?=\]\])', p_score_str)
            match2 = re.search(r'(?<=评分\*\*[:：]\[\[)\d+(?=\]\])', p_score_str)
            match3 = re.search(r'(?<=评分[:：] \[\[)\d+(?=\]\])', p_score_str)
            match4 = re.search(r'(?<=评分\*\*[:：] \[\[)\d+(?=\]\])', p_score_str)
            if match:
                rating = int(match.group())
            elif match2:
                rating = int(match2.group())
            elif match3:
                rating = int(match3.group())
            elif match4:
                rating = int(match4.group())
            else:
                rating = 1
            return rating

        processed = set()
        scores = {}

        if os.path.exists(p_res_path):
            with open(p_res_path, mode="r", encoding="utf-8") as f:
                lines = f.readlines()
            for tl in lines:
                tr = json.loads(tl)
                processed.add(tr['trace_id'])
                if tr['category'] not in scores:
                    scores[tr['category']] = []
                scores[tr['category']].append(ext_score(tr['gpt_score_result'][0]))

        for t_sample in tqdm(p_samples):
            if t_sample['trace_id'] in processed:
                continue
            t_prompt = t_sample["gpt_score_prompt"]
            t_prompt = t_prompt[0].replace("{answer}", t_sample['response'])
            t_prompt = t_prompt.replace("{prompt}", str(t_sample['messages']))
            t_prompt = t_prompt.replace("{std}", t_sample['reference'])
            if isinstance(self.model, GptIntApi):
                gpt_score = self._internal_model_generate(t_sample.get('trace_id', ''), t_prompt)
            else:
                gpt_score = self._model_generate(t_prompt)
            t_sample['gpt_score_result'] = [gpt_score]

            score = ext_score(gpt_score)

            t_sample['score'] = [score]
            if t_sample['category'] not in scores:
                scores[t_sample['category']] = []
            scores[t_sample['category']].append(score)

            fw = open(p_res_path, mode="a", encoding="utf-8")
            fw.write(json.dumps(t_sample, ensure_ascii=False) + "\n")
            fw.close()

        score_list = list()
        ret_score = {}
        for k, v in scores.items():
            print(f"{k}: {sum(v) / len(v)}")
            score_list.append(sum(v) / len(v))
            ret_score[k] = sum(v) / len(v)

        ret_score["score"] = sum(score_list) / len(score_list)
        print(f"总分: {sum(score_list) / len(score_list)}")
        return ret_score
    def score(self, p_samples: List[Dict], p_res_path: str):
        if len(p_samples) == 0:
            return None

        if p_samples[0]['eval_set_name'] == 'MtBench' or p_samples[0]['eval_set_name'] == 'ZhMtBench':
            ret = self._score_mt_bench(p_samples, p_res_path)
        elif p_samples[0]['eval_set_name'] == 'MT_Eval':
            ret = self._score_MT_eval(p_samples, p_res_path)
        else:
            ret = self._common_gpt_score(p_samples, p_res_path)

        print(f"finish score res path is {p_res_path}")
        return ret
