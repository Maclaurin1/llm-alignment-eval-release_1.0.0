# coding: utf-8
# @author: kaimin
# @time: 2024-01-22 13:38
import json
import os
import pandas

ds_name = "cmmlu"
base_dir = "../data/cmmlu/"
dev_files = os.listdir(os.path.join(base_dir, "dev"))
test_files = os.listdir(os.path.join(base_dir, "test"))

cmmlu_subject_mapping = {
    'agronomy': '农学',
    'anatomy': '解剖学',
    'ancient_chinese': '古汉语',
    'arts': '艺术学',
    'astronomy': '天文学',
    'business_ethics': '商业伦理',
    'chinese_civil_service_exam': '中国公务员考试',
    'chinese_driving_rule': '中国驾驶规则',
    'chinese_food_culture': '中国饮食文化',
    'chinese_foreign_policy': '中国外交政策',
    'chinese_history': '中国历史',
    'chinese_literature': '中国文学',
    'chinese_teacher_qualification': '中国教师资格',
    'clinical_knowledge': '临床知识',
    'college_actuarial_science': '大学精算学',
    'college_education': '大学教育学',
    'college_engineering_hydrology': '大学工程水文学',
    'college_law': '大学法律',
    'college_mathematics': '大学数学',
    'college_medical_statistics': '大学医学统计',
    'college_medicine': '大学医学',
    'computer_science': '计算机科学',
    'computer_security': '计算机安全',
    'conceptual_physics': '概念物理学',
    'construction_project_management': '建设工程管理',
    'economics': '经济学',
    'education': '教育学',
    'electrical_engineering': '电气工程',
    'elementary_chinese': '小学语文',
    'elementary_commonsense': '小学常识',
    'elementary_information_and_technology': '小学信息技术',
    'elementary_mathematics': '初等数学',
    'ethnology': '民族学',
    'food_science': '食品科学',
    'genetics': '遗传学',
    'global_facts': '全球事实',
    'high_school_biology': '高中生物',
    'high_school_chemistry': '高中化学',
    'high_school_geography': '高中地理',
    'high_school_mathematics': '高中数学',
    'high_school_physics': '高中物理学',
    'high_school_politics': '高中政治',
    'human_sexuality': '人类性行为',
    'international_law': '国际法学',
    'journalism': '新闻学',
    'jurisprudence': '法理学',
    'legal_and_moral_basis': '法律与道德基础',
    'logical': '逻辑学',
    'machine_learning': '机器学习',
    'management': '管理学',
    'marketing': '市场营销',
    'marxist_theory': '马克思主义理论',
    'modern_chinese': '现代汉语',
    'nutrition': '营养学',
    'philosophy': '哲学',
    'professional_accounting': '专业会计',
    'professional_law': '专业法学',
    'professional_medicine': '专业医学',
    'professional_psychology': '专业心理学',
    'public_relations': '公共关系',
    'security_study': '安全研究',
    'sociology': '社会学',
    'sports_science': '体育学',
    'traditional_chinese_medicine': '中医中药',
    'virology': '病毒学',
    'world_history': '世界历史',
    'world_religions': '世界宗教'
}

prompt = "以下是关于{subject}的单项选择题，请直接给出正确答案的选项。\n题目：{question}\nA. {A}\nB. {B}\nC. {C}\nD. {D}\n答案是: "

dev_data_map = dict()

for tf in dev_files:
    t_sub = tf.replace(".csv", "")
    t_sub_name = cmmlu_subject_mapping[t_sub][1]

    dev_data = pandas.read_csv(os.path.join(base_dir, "dev", tf))

    samples = list()
    for td in dev_data.iterrows():
        samples.append(prompt.format(
            subject=t_sub_name,
            question=td[1]['Question'],
            A=td[1]['A'],
            B=td[1]['B'],
            C=td[1]['C'],
            D=td[1]['D'],
        ) + td[1]['Answer'])
    dev_data_map[t_sub] = samples

data_list = list()

for tf in test_files:
    t_sub = tf.replace(".csv", "")
    t_sub_name = cmmlu_subject_mapping[t_sub][1]
    val_data = pandas.read_csv(os.path.join(base_dir, "test", tf))

    for td in val_data.iterrows():
        t_query = "\n".join(dev_data_map[t_sub][0: 3]) + "\n" + prompt.format(
            subject=t_sub_name,
            question=td[1]['Question'],
            A=td[1]['A'],
            B=td[1]['B'],
            C=td[1]['C'],
            D=td[1]['D'],
        )

        md = {
            "id": t_sub + "_" + str(td[1][0]).zfill(8),
            "query": t_query,
            "answer": td[1]['Answer'],
            "type_list": [cmmlu_subject_mapping[t_sub]]
        }

        data_list.append(md)

fw = open(f"./eval_data/cmmlu_3shots_test_{len(data_list)}.json", mode="w", encoding="utf-8")
json.dump(data_list, fw, ensure_ascii=False, indent=2)
fw.close()
