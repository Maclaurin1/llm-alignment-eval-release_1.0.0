# coding: utf-8
# @author: kaimin
# @time: 2024-01-22 16:08
import json

prompt = 'Complete the following python code:\n{prompt}'

fr = open("../data/openai_humaneval/human-eval.jsonl", mode="r", encoding="utf-8")
lines = fr.readlines()
fr.close()
count = 0
data_list = list()

for tl in lines:
    td = json.loads(tl)
    t_query = prompt.format(prompt=td['prompt'])

    md = {
        "id": td['task_id'],
        "query": t_query,
        "answer": {
            "entry_point": td['entry_point'],
            "canonical_solution": td['canonical_solution'],
            "test": td['test'],
        },
        "type_list": ["humaneval"]
    }
    data_list.append(md)
    count += 1

fw = open(f"./eval_data/humaneval_{len(data_list)}.json", mode="w", encoding="utf-8")
json.dump(data_list, fw, ensure_ascii=False, indent=2)
fw.close()
