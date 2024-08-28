# coding: utf-8
# @author: kaimin
# @time: 2024-01-22 14:04
import json
import os
import pandas

ds_name = "mmlu"
base_dir = "../data/mmlu/"
dev_files = os.listdir(os.path.join(base_dir, "dev"))
test_files = os.listdir(os.path.join(base_dir, "test"))

prompt = "There is a single choice question about {subject}. Answer the question by replying A, B, C or D.\n\nQuestion: {question}\nA. {A}\nB. {B}\nC. {C}\nD. {D}\nAnswer: "

dev_data_map = dict()

for tf in dev_files:
    t_sub = tf.replace("_dev.csv", "")
    t_sub_name = t_sub.replace("_", " ")
    dev_data = pandas.read_csv(os.path.join(base_dir, "dev", tf), header=None)

    samples = list()
    for td in dev_data.iterrows():
        samples.append(prompt.format(
            subject=t_sub_name,
            question=td[1][0],
            A=td[1][1],
            B=td[1][2],
            C=td[1][3],
            D=td[1][4],
        ) + td[1][5])
    dev_data_map[t_sub] = samples

data_list = list()

for tf in test_files:
    t_sub = tf.replace("_test.csv", "")
    t_sub_name = t_sub.replace("_", " ")
    val_data = pandas.read_csv(os.path.join(base_dir, "test", tf), header=None)
    count = 0

    for td in val_data.iterrows():
        t_query = "\n".join(dev_data_map[t_sub][0: 3]) + "\n" + prompt.format(
            subject=t_sub_name,
            question=td[1][0],
            A=td[1][1],
            B=td[1][2],
            C=td[1][3],
            D=td[1][4],
        )

        md = {
            "id": t_sub + "_" + str(count).zfill(8),
            "query": t_query,
            "answer": td[1][5],
            "type_list": [t_sub_name]
        }

        data_list.append(md)
        count += 1

fw = open(f"./eval_data/mmlu_3shots_test_{len(data_list)}.json", mode="w", encoding="utf-8")
json.dump(data_list, fw, ensure_ascii=False, indent=2)
fw.close()
