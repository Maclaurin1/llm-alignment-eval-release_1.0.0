# coding: utf-8
# @author: kaimin
# @time: 2024-01-22 17:05
import datetime
import json
import os
from queue import Queue
from typing import List, Dict

from alignment_eval.utils.mx_generation_utils import is_blank
from alignment_eval.models import BaseApi, Conversation


class GenerateManager(object):
    def __init__(
            self,
            p_output_dir: str,
            p_data_path: str,
            p_model_name: str,
            p_model: BaseApi,
    ):
        self.output_dir = p_output_dir
        self.data_path = p_data_path
        self.model_name = p_model_name
        self.model = p_model

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.model_output_dir = os.path.join(self.output_dir, self.model_name)
        if not os.path.exists(self.model_output_dir):
            os.makedirs(self.model_output_dir)

    def _generate(self, p_eval_data: List[Dict]):
        t_query_list = list()
        for td in p_eval_data:
            t_query_list.append(Conversation(td))
        t_res = self.model.generate_batch(t_query_list)
        return t_res

    @staticmethod
    def check_finish(p_messages):
        is_finish = True

        if p_messages.get("response") is None:
            is_finish = False

        for t_msg in p_messages['messages']:
            if t_msg['role'] == 'assistant' and t_msg.get("content") is None:
                is_finish = False
                break

        return is_finish

    @staticmethod
    def split_input(p_messages):
        cur_input = p_messages.copy()
        cur_input['messages'] = []

        for t_msg in p_messages['messages']:
            if t_msg['role'] == 'assistant' and is_blank(t_msg.get("content")):
                break
            cur_input['messages'].append(t_msg)

        return cur_input

    @staticmethod
    def add_assistant_response(p_messages, p_response):
        is_finish = False

        for t_msg in p_messages['messages']:
            if t_msg['role'] == 'assistant' and is_blank(t_msg.get("content")):
                t_msg['content'] = p_response
                is_finish = True
                break
        if not is_finish and is_blank(p_messages.get("response")):
            p_messages['response'] = p_response

        return p_messages

    def do_generate(self):
        results_path = os.path.join(self.model_output_dir, f"{self.model_name}_results.jsonl")

        processed = set()
        with open(self.data_path, mode="r", encoding="utf-8") as f:
            eval_data_list = json.load(f)

        if os.path.exists(results_path):
            with open(results_path, mode="r", encoding="utf-8") as f:
                lines = f.readlines()
            for tl in lines:
                tr = json.loads(tl)
                processed.add(tr['trace_id'])

        eval_data_queue = Queue()
        eval_message_data = list()
        eval_data = list()

        # 判断是否完成，完成写文件
        # 未完成切输入
        # 组队调用模型
        # 回填答案到第一个none或者response
        for td in eval_data_list:
            if td['trace_id'] not in processed:
                eval_data_queue.put(td)

        check_count = 0
        finish_count = 0

        while not eval_data_queue.empty():
            t_msg = eval_data_queue.get()
            cur_input = self.split_input(t_msg)
            check_count += 1
            print(f"checked {check_count}")
            eval_data.append(cur_input)
            eval_message_data.append(t_msg)

            if len(eval_data) == self.model.workers:
                t_responses = self._generate(eval_data)
                for i, tr in enumerate(t_responses):
                    m_msg = self.add_assistant_response(eval_message_data[i], tr)
                    is_finish = self.check_finish(m_msg)

                    if is_finish:
                        finish_count += 1
                        print(f"finished {finish_count}")
                        fw = open(results_path, mode="a", encoding="utf-8")
                        fw.write(json.dumps(m_msg, ensure_ascii=False) + "\n")
                        fw.close()
                    else:
                        eval_data_queue.put(m_msg)
                eval_data.clear()
                eval_message_data.clear()

        if len(eval_data) > 0:
            t_responses = self._generate(eval_data)
            for i, tr in enumerate(t_responses):
                m_msg = self.add_assistant_response(eval_message_data[i], tr)
                is_finish = self.check_finish(m_msg)

                if is_finish:
                    finish_count += 1
                    print(f"finished {finish_count}")
                    fw = open(results_path, mode="a", encoding="utf-8")
                    fw.write(json.dumps(m_msg, ensure_ascii=False) + "\n")
                    fw.close()
                else:
                    eval_data_queue.put(m_msg)
            eval_data.clear()
            eval_message_data.clear()

            while not eval_data_queue.empty():
                t_msg = eval_data_queue.get()
                cur_input = self.split_input(t_msg)
                check_count += 1
                print(f"checked {check_count}")
                eval_data.append(cur_input)
                eval_message_data.append(t_msg)

                t_responses = self._generate(eval_data)
                for i, tr in enumerate(t_responses):
                    m_msg = self.add_assistant_response(eval_message_data[i], tr)
                    is_finish = self.check_finish(m_msg)

                    if is_finish:
                        finish_count += 1
                        print(f"finished {finish_count}")
                        fw = open(results_path, mode="a", encoding="utf-8")
                        fw.write(json.dumps(m_msg, ensure_ascii=False) + "\n")
                        fw.close()
                    else:
                        eval_data_queue.put(m_msg)
                eval_data.clear()
                eval_message_data.clear()

    def do_eval(self):
        pass
