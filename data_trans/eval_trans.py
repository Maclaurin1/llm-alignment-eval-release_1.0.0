# coding: utf-8
# @author: kaimin
# @time: 2024-01-30 10:08
import hashlib
import json
from alignment_eval.utils.mx_generation_utils import build_qa_list, is_blank

fr = open("../eval_data/AllEval_240117_with_system.json", mode="r", encoding="utf-8")
data = json.load(fr)
fr.close()

data_list = list()

for td in data:
    if not is_blank(td['input']):
        t_msgs = build_qa_list(td['instruction'] + "\n" + td['input'])
    else:
        t_msgs = build_qa_list(td['instruction'])
    if is_blank(td['id']):
        t_id = "test_" + hashlib.md5((td['instruction'] + "\n" + td['input']).strip().encode(encoding='utf-8')).hexdigest()
    else:
        t_id = td['id']

    md = {
        "trace_id": t_id,
        "system_content": "你的名字是妙想，你是东方财富公司自主研发的金融行业大语言模型，来帮助用户获取有用信息。\n你的训练数据截止时间为2023年，当前时间为{cur_time}。",
        "messages": t_msgs,
        "top_p": 0.85,
        "top_k": 5,
        "temperature": 0.3,
        "max_tokens": 1024,
    }
    data_list.append(md)

fw = open("../compare_data/chat_base_tests_240130.json", mode="w", encoding="utf-8")
json.dump(data_list, fw, ensure_ascii=False, indent=2)
fw.close()