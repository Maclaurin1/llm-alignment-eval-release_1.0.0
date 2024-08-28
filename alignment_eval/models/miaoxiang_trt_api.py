# coding: utf-8
# @author: kaimin
# @time: 2024-05-08 13:55
import json
import re

import requests

from concurrent.futures import ThreadPoolExecutor
from typing import List
from transformers import AutoTokenizer

from alignment_eval.models.base_api import BaseApi
from alignment_eval.models.conversation import Conversation
from alignment_eval.utils.mx_generation_utils import build_inputs


class MxTrtApi(BaseApi):
    def __init__(self, model: str, token: str, tokenizer_path: str, workers: int = 4, retry: int = 2):
        super().__init__(model, retry)
        self.workers = workers
        self.token = token
        self.tokenizer_path = tokenizer_path
        self.mx_tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True, use_fast=False)

    def generate_single(self, data: Conversation) -> str:
        return self._generate_stream_api(data)

    def generate_batch(self, data_list: List[Conversation]) -> List[str]:
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            results = list(executor.map(self._generate_stream_api, data_list))
        return results

    def _generate_stream_api(self, data: Conversation, ignore_error: bool = False) -> str:
        headers = {
            'content-type': 'application/json',
            'Authorization': self.token
        }

        t_msgs = []
        for t_msg in data.messages:
            t_msgs.append((t_msg['role'], t_msg['content']))
        prompt_token_ids = build_inputs(messages=t_msgs, tokenizer=self.mx_tokenizer, system_content=data.system_content)
        json_datas = {
            "text_input": " ".join(list(map(str, prompt_token_ids))),
            "max_tokens": data.generate_args.max_new_tokens,
            "top_p": data.generate_args.top_p,
            "top_k": data.generate_args.top_k,
            "temperature": data.generate_args.temperature,
            "stream": True
        }

        max_num_retries = 0
        while max_num_retries < self.retry:
            try:
                response = requests.post(self.model, json=json_datas, headers=headers, stream=True)
            except:
                max_num_retries += 1
                print('Got connection error, retrying...')
                print(json.dumps(json_datas, ensure_ascii=False, indent=2))
                continue
            try:
                all_tokens = []
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    ck = chunk.decode()
                    datas = json.loads(ck[ck.find("{"):ck.find("}") + 1])
                    token = datas["text_output"].strip("[").rstrip("]")
                    if len(token) > 0:
                        token = int(token)
                        all_tokens.append(token)

                response = self.mx_tokenizer.decode(all_tokens)
                return response
            except:
                print(json.dumps(json_datas, ensure_ascii=False, indent=2))
                print('Find error message in response: ', str(response.text))
            max_num_retries += 1

        if ignore_error:
            return ""
        else:
            raise RuntimeError('Calling EM API failed after retrying for ' f'{max_num_retries} times. Check the logs for details.')

    def _generate(self, data: Conversation, ignore_error: bool = False) -> str:
        headers = {
            'content-type': 'application/json',
            'Authorization': self.token
        }

        t_msgs = []
        for t_msg in data.messages:
            t_msgs.append((t_msg['role'], t_msg['content']))
        prompt_token_ids = build_inputs(messages=t_msgs, tokenizer=self.mx_tokenizer, system_content=data.system_content)
        json_datas = {
            "text_input": " ".join(list(map(str, prompt_token_ids))),
            "max_tokens": data.generate_args.max_new_tokens,
            "top_p": data.generate_args.top_p,
            "top_k": data.generate_args.top_k,
            "temperature": data.generate_args.temperature
        }

        max_num_retries = 0
        while max_num_retries < self.retry:
            try:
                response = requests.post(self.model, json=json_datas, headers=headers)
            except:
                max_num_retries += 1
                print('Got connection error, retrying...')
                print(json.dumps(json_datas, ensure_ascii=False, indent=2))
                continue
            try:
                res = json.loads(response.text[5:])
                if res.get('text_output') is not None:
                    output_tokens = res['text_output']
                    # 去除字符串中的换行符'\n'
                    output_tokens = output_tokens.replace('\n', '')
                    # 将多个空格替换为一个空格
                    output_tokens = re.sub(' +', ' ', output_tokens)
                    # 将空格替换为逗号
                    output_tokens = output_tokens.replace(' ', ',').replace("[,", "[").replace(",]", ",")
                    output_tokens = json.loads(output_tokens)
                    output_tokens = output_tokens[len(prompt_token_ids):]
                    response = self.mx_tokenizer.decode(output_tokens)
                    return response
            except:
                print(json.dumps(json_datas, ensure_ascii=False, indent=2))
                print('Find error message in response: ', str(response.text))
            max_num_retries += 1

        if ignore_error:
            return ""
        else:
            raise RuntimeError('Calling EM API failed after retrying for ' f'{max_num_retries} times. Check the logs for details.')
