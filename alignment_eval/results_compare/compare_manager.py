# coding: utf-8
# @author: kaimin
# @time: 2024-05-15 09:51
import json
import os.path

from alignment_eval.models import QwenApi
from alignment_eval.results_compare.compare_objects import CompareParts

COMMON_DESC_PROMPT = """按照表格数据进行总结描述，表格中是两个模型在评估集上的对比效果，概括说说两个模型的表现和哪个模型更有优势。
总结为一段话300字以内，重点部分加粗表示。
"""


class CompareManager:
    def __init__(self, p_out_dir1, p_out_dir2, p_model_name1, p_model_name2, p_qw_url, p_qw_token):
        self.out_dir1 = p_out_dir1
        self.out_dir2 = p_out_dir2
        self.model_name1 = p_model_name1
        self.model_name2 = p_model_name2

        self.model1_scores = {}
        self.model2_scores = {}

        self._data_load()
        self.model = QwenApi(model=p_qw_url, token=p_qw_token, workers=4, retry=2)

    def _data_load(self):
        def score_file_process(p_score_json_data, p_out_dir, p_model_name):
            key_map = {
                "abcEval":"客观题能力",
                "CDME": "大海捞针-填空",
                "CDME_NF": "大海捞针-问答",
                "IFEval": "IFEval",
                "RAIFB_api1_part1": "自建RAG金融-sys",
                "RAIFB_api1_part2": "自建RAG通用-sys",
                "RAIFB_api1_part3": "自建RAG技术-sys",
                "RAIFB_api2_part1": "自建RAG金融-msg",
                "RAIFB_api2_part2": "自建RAG通用-msg",
                "RAIFB_api2_part3": "自建RAG技术-msg",
                "ZhIFEval": "ZhIFEval",
                "ceval": "ceval",
                "emfin": "金融自建选择",
                "mmlu": "mmlu",
                "gsm": "gsm",
                "score": "综合评分",
                "Prompt-level-strict-accuracy": "完整指令严格",
                "Inst-level-strict-accuracy": "单条指令严格",
                "Prompt-level-loose-accuracy": "完整指令宽松",
                "Inst-level-loose-accuracy": "单条指令宽松",
                "Prompt-level-if_strict-accuracy": "完整指令严格",
                "Inst-level-if_strict-accuracy": "单条指令严格",
                "Prompt-level-if_loose-accuracy": "完整指令宽松",
                "Inst-level-if_loose-accuracy": "单条指令宽松",
                "rag_strict": "rag严格匹配要点",
                "rag_loose": "rag宽松匹配要点（rouge-L）",
            }

            sum_map = {
                "整体效果评估": {
                    "score_results": {}
                }
            }
            for k, v in p_score_json_data.items():
                sum_map["整体效果评估"]["score_results"][key_map[k]] = v['score']
                sub_key = f"{key_map[k]}详细结果"
                sum_map[sub_key] = {}
                sum_map[sub_key]["score_results"] = {}
                for tsk, tsv in v.items():
                    if tsk in key_map:
                        tsk = key_map.get(tsk)
                    sum_map[sub_key]["score_results"][tsk] = tsv
                    if k == "CDME" or k == "CDME_NF" or k == "abcEval":
                        dt_path = os.path.join(p_out_dir, f"{p_model_name}_{k}.png")
                    else:
                        dt_path = os.path.join(p_out_dir, f"{p_model_name}_{k}.json")
                    if os.path.exists(dt_path):
                        sum_map[sub_key]['detail_file_path'] = dt_path

            return sum_map

        t_score_file_path = os.path.join(self.out_dir1, "scores_sum.json")
        if os.path.exists(t_score_file_path):
            fr = open(t_score_file_path, mode="r", encoding="utf-8")
            t_data = json.load(fr)
            fr.close()
            self.model1_scores = score_file_process(t_data, self.out_dir1, self.model_name1)
        else:
            raise RuntimeError(f"No scores sum file {t_score_file_path}")

        t_score_file_path = os.path.join(self.out_dir2, "scores_sum.json")
        if os.path.exists(t_score_file_path):
            fr = open(t_score_file_path, mode="r", encoding="utf-8")
            t_data = json.load(fr)
            fr.close()
            self.model2_scores = score_file_process(t_data, self.out_dir2, self.model_name2)
        else:
            raise RuntimeError(f"No scores sum file {t_score_file_path}")

    def gen_compare_result(self):
        res = ""
        counter = 0

        for k, v in self.model1_scores.items():
            if k in self.model2_scores:
                t_data = {
                    self.model_name1: v,
                    self.model_name2: self.model2_scores[k]
                }
                counter += 1
                if "大海捞针" in k:
                    tcp = CompareParts(f"{counter}. {k}", t_data, COMMON_DESC_PROMPT)
                    res += tcp.get_ed_sp_desc_content(self.model)
                else:
                    tcp = CompareParts(f"{counter}. {k}", t_data, COMMON_DESC_PROMPT)
                    res += tcp.get_data_with_desc_content(self.model)
                    res += tcp.get_compare_samples()

                print(f"{counter}. {k} finished")

        return res