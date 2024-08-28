# coding: utf-8
# @author: kaimin
# @time: 2024-01-22 14:47
import json
import os
import pandas

ds_name = "BBH"
base_dir = "../data/BBH/"
test_files = os.listdir(os.path.join(base_dir, "data"))

prompt = "Follow the given examples and answer the question.\n{hint}\n\nQ: {question}\nA: Let's think step by step."

data_list = list()
for tf in test_files:
    count = 0
    t_sub = tf.replace(".json", "")
    t_sub_name = t_sub.replace("_", " ")
    with open(os.path.join(base_dir, 'data', f'{t_sub}.json'), 'r') as f:
        val_data = json.load(f)
    with open(os.path.join(base_dir, 'lib_prompt', f'{t_sub}.txt'), 'r') as f:
        hint = f.read()

    for td in val_data['examples']:
        t_query = prompt.format(
            hint=hint,
            question=td['input'],
        )

        md = {
            "id": t_sub + "_" + str(count).zfill(8),
            "query": t_query,
            "answer": td['target'],
            "type_list": [t_sub_name]
        }

        data_list.append(md)
        count += 1

fw = open(f"./eval_data/bbh_3shots_{len(data_list)}.json", mode="w", encoding="utf-8")
json.dump(data_list, fw, ensure_ascii=False, indent=2)
fw.close()
