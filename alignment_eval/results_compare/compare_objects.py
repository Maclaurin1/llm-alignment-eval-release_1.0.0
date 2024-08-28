# coding: utf-8
# @author: kaimin
# @time: 2024-05-15 09:01
import json
import random
from typing import Dict

from alignment_eval.models import BaseApi, Conversation

table_dec_map = {
    "大海捞针": "大海捞针测试是评估大型语言模型处理海量文本能力的实验，通过将关键信息隐藏在大量文本中来检验模型的识别和提取准确性。在该测试中，\"Length\"指文本的总长度或token数，而\"Depth\"表示信息的嵌入的深度，两者共同决定了测试的难度和模型处理长文本的能力。表格中给出的数据是模型在给定文本长度和信息深度下的准确率。",
    "IFEval": "IFEval（Instruction-Following Evaluation）是一种用于评估大型语言模型（LLM）指令跟随能力的评估基准。它专注于一组“可验证的指令”，这些指令是那些可以明确判断模型是否遵循的指令。表格中给出的是不同维度评估的准确率，综合评分是完整指令宽松和单条指令严格的均值。",
    "自建RAG金融": "自建金融从指令跟随和搜索增强两方面评估，指令跟随是格式要求的跟随能力，分为完整指令严格、单条指令严格、完整指令宽松和单条指令宽松四个方面。搜索增强评估了模型按照信息回答问题的能力，按照严格匹配和算rouge综合评定。",
    "金融自建选择": "评估模型金融能力，表格中是每个类型的准确率，综合评分是各个类型的准确率均值。",
    "ceval": "C-Eval是一个全面的中文基础模型评估套件，旨在帮助开发者更好地开发中文大模型，促进学术界和产业界科学地使用该评估套件帮助模型迭代。表格中是每个类型的准确率，综合评分是各个类型的准确率均值。",
    "mmlu": "mmlu是一个全面的英文基础模型评估套件，旨在帮助开发者更好地开发英文大模型，促进学术界和产业界科学地使用该评估套件帮助模型迭代。表格中是每个类型的准确率，综合评分是各个类型的准确率均值。",
    "gsm": "GSM是一个由OpenAI发布的数据集，专门用于评估大型语言模型（LLMs）在数学推理任务上的表现。评分为答题准确率。"
}


class CompareParts(object):

    def __init__(self, p_index: str, p_compare_data: Dict, p_desc_prompt: str):
        # 小标题index
        self.index = p_index
        # {"model_name1": {score info}, "model_name2": {score info}}
        self.compare_data = p_compare_data
        self.desc_prompt = p_desc_prompt

    def _data_to_mdtable(self):
        """
        key | model1 | model2
        :return:
        """
        if isinstance(self.compare_data, str):
            t_data = json.loads(self.compare_data)
        else:
            t_data = self.compare_data

        data = {}
        for k, v in t_data.items():
            data[k] = v['score_results']

        # Prepare the header of the Markdown table
        header = "| 指标 | " + " | ".join(data.keys()) + " |\n"
        separator = "| --- " * (len(data) + 1) + "|\n"
        markdown_table = header + separator

        # Determine the unique set of keys across all models
        all_keys = set()
        for scores in data.values():
            all_keys.update(scores.keys())
        all_keys = sorted(list(all_keys))

        # Fill the table rows with the corresponding scores
        for key in all_keys:
            row = f"| {key} "
            for model in data.values():
                # Use the score if it exists, otherwise use a placeholder (e.g., "N/A")
                score = model.get(key, "N/A")
                if score != "N/A":
                    score = "{:.3f}".format(score)
                row += f"| {score} "
            row += "|\n"
            markdown_table += row

        return markdown_table

    def _get_table_desc(self, p_model):
        table = self._data_to_mdtable()
        table_dec = ""
        for k, v in table_dec_map.items():
            if k in self.index:
                table_dec = table_dec_map[k]
                break

        m_dt = {
            "trace_id": self.index,
            "system_content": "You are an AI assistant that helps people find information.",
            "messages": [{"role": "user", "content": table + f"\n\n{table_dec}\n\n" + self.desc_prompt}]
        }
        t_cov = Conversation(m_dt)
        dec = p_model.generate_single(t_cov).strip()

        return dec

    def get_data_content(self):
        content = "# " + self.index + "\n\n"
        content += self._data_to_mdtable() + "\n\n"
        return content

    def get_data_with_desc_content(self, p_model: BaseApi):
        content = "# " + self.index + "\n\n"

        table = self._data_to_mdtable()
        dec = self._get_table_desc(p_model)

        content += dec + "\n\n"
        content += table + "\n\n"

        return content

    def get_ed_sp_content(self):
        content = "# " + self.index + "\n\n"
        for k, v in self.compare_data.items():
            content += f"![大海捞针对比图]({self.compare_data[k]['detail_file_path']} \"大海捞针对比图\")\n\n{k}\n\n"
        return content

    def get_ed_sp_desc_content(self, p_model):
        dec = self._get_table_desc(p_model)
        content = "# " + self.index + "\n\n" + dec + "\n\n"
        for k, v in self.compare_data.items():
            content += f"![大海捞针对比图]({self.compare_data[k]['detail_file_path']} \"大海捞针对比图\")\n\n{k}\n\n"
        return content

    def get_compare_samples(self, p_num=2):
        def to_kv_map(p_list):
            ret_dict = {}
            for tl in p_list:
                ret_dict[tl['trace_id']] = tl
            return ret_dict

        files = []
        models = []

        for k, v in self.compare_data.items():
            models.append(k)
            if 'detail_file_path' not in v:
                return ""
            files.append(v['detail_file_path'])

        if len(files) != 2:
            raise RuntimeError("Only compare 2")

        data_list = []
        for tf in files:
            fr = open(tf, mode="r", encoding="utf-8")
            t_data = json.load(fr)
            data_list.append(to_kv_map(t_data))

        better0 = []
        better1 = []

        keys = list(data_list[0].keys())
        random.shuffle(keys)
        for tk in keys:
            if tk not in data_list[0] or tk not in data_list[1]:
                continue
            t_smp0 = data_list[0][tk]
            t_smp1 = data_list[1][tk]
            if t_smp0['score'] > t_smp1['score']:
                better0.append([t_smp0, t_smp1])
            if len(better0) >= p_num:
                break

        for tk in keys:
            if tk not in data_list[0] or tk not in data_list[1]:
                continue

            t_smp0 = data_list[0][tk]
            t_smp1 = data_list[1][tk]
            if t_smp1['score'] > t_smp0['score']:
                better1.append([t_smp0, t_smp1])
            if len(better1) >= p_num:
                break

        ret_content = ""
        if len(better0) > 0:
            ret_content += f"## {models[0]}优于{models[1]}的例子\n\n"
            counter = 0
            for t_bs in better0:
                counter += 1
                if 'reference' in t_bs[0]:
                    ret_content += f"```sample{counter}\n题目ID: {t_bs[0]['trace_id']}\n\n参考答案: {t_bs[0]['reference']}\n\n{models[0]}输出: {t_bs[0]['response']}\n\n{models[1]}输出: {t_bs[1]['response']}\n```\n\n"
                else:
                    ret_content += f"```sample{counter}\n题目ID: {t_bs[0]['trace_id']}\n\n{models[0]}输出: {t_bs[0]['response']}\n\n{models[1]}输出: {t_bs[1]['response']}\n```\n\n"

        if len(better1) > 0:
            ret_content += f"## {models[1]}优于{models[0]}的例子\n\n"
            counter = 0
            for t_bs in better1:
                counter += 1
                if 'reference' in t_bs[0]:
                    ret_content += f"```sample{counter}\n题目ID: {t_bs[0]['trace_id']}\n\n参考答案: {t_bs[0]['reference']}\n\n{models[1]}输出: {t_bs[1]['response']}\n\n{models[0]}输出: {t_bs[0]['response']}\n```\n\n"
                else:
                    ret_content += f"```sample{counter}\n题目ID: {t_bs[0]['trace_id']}\n\n{models[1]}输出: {t_bs[1]['response']}\n\n{models[0]}输出: {t_bs[0]['response']}\n```\n\n"

        return ret_content
