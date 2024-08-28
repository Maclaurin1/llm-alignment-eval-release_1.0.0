# coding: utf-8
# @author: kaimin
# @time: 2024-01-22 10:52
import json
import os
import pandas

ds_name = "ceval"
base_dir = "../data/ceval/formal_ceval"
dev_files = os.listdir(os.path.join(base_dir, "dev"))
val_files = os.listdir(os.path.join(base_dir, "val"))

ceval_subject_mapping = {
    'computer_network': ['Computer Network', '计算机网络', 'STEM'],
    'operating_system': ['Operating System', '操作系统', 'STEM'],
    'computer_architecture': ['Computer Architecture', '计算机组成', 'STEM'],
    'college_programming': ['College Programming', '大学编程', 'STEM'],
    'college_physics': ['College Physics', '大学物理', 'STEM'],
    'college_chemistry': ['College Chemistry', '大学化学', 'STEM'],
    'advanced_mathematics': ['Advanced Mathematics', '高等数学', 'STEM'],
    'probability_and_statistics': ['Probability and Statistics', '概率统计', 'STEM'],
    'discrete_mathematics': ['Discrete Mathematics', '离散数学', 'STEM'],
    'electrical_engineer': ['Electrical Engineer', '注册电气工程师', 'STEM'],
    'metrology_engineer': ['Metrology Engineer', '注册计量师', 'STEM'],
    'high_school_mathematics': ['High School Mathematics', '高中数学', 'STEM'],
    'high_school_physics': ['High School Physics', '高中物理', 'STEM'],
    'high_school_chemistry': ['High School Chemistry', '高中化学', 'STEM'],
    'high_school_biology': ['High School Biology', '高中生物', 'STEM'],
    'middle_school_mathematics': ['Middle School Mathematics', '初中数学', 'STEM'],
    'middle_school_biology': ['Middle School Biology', '初中生物', 'STEM'],
    'middle_school_physics': ['Middle School Physics', '初中物理', 'STEM'],
    'middle_school_chemistry': ['Middle School Chemistry', '初中化学', 'STEM'],
    'veterinary_medicine': ['Veterinary Medicine', '兽医学', 'STEM'],
    'college_economics': ['College Economics', '大学经济学', 'Social Science'],
    'business_administration': ['Business Administration', '工商管理', 'Social Science'],
    'marxism': ['Marxism', '马克思主义基本原理', 'Social Science'],
    'mao_zedong_thought': ['Mao Zedong Thought', '毛泽东思想和中国特色社会主义理论体系概论', 'Social Science'],
    'education_science': ['Education Science', '教育学', 'Social Science'],
    'teacher_qualification': ['Teacher Qualification', '教师资格', 'Social Science'],
    'high_school_politics': ['High School Politics', '高中政治', 'Social Science'],
    'high_school_geography': ['High School Geography', '高中地理', 'Social Science'],
    'middle_school_politics': ['Middle School Politics', '初中政治', 'Social Science'],
    'middle_school_geography': ['Middle School Geography', '初中地理', 'Social Science'],
    'modern_chinese_history': ['Modern Chinese History', '近代史纲要', 'Humanities'],
    'ideological_and_moral_cultivation': ['Ideological and Moral Cultivation', '思想道德修养与法律基础', 'Humanities'],
    'logic': ['Logic', '逻辑学', 'Humanities'],
    'law': ['Law', '法学', 'Humanities'],
    'chinese_language_and_literature': ['Chinese Language and Literature', '中国语言文学', 'Humanities'],
    'art_studies': ['Art Studies', '艺术学', 'Humanities'],
    'professional_tour_guide': ['Professional Tour Guide', '导游资格', 'Humanities'],
    'legal_professional': ['Legal Professional', '法律职业资格', 'Humanities'],
    'high_school_chinese': ['High School Chinese', '高中语文', 'Humanities'],
    'high_school_history': ['High School History', '高中历史', 'Humanities'],
    'middle_school_history': ['Middle School History', '初中历史', 'Humanities'],
    'civil_servant': ['Civil Servant', '公务员', 'Other'],
    'sports_science': ['Sports Science', '体育学', 'Other'],
    'plant_protection': ['Plant Protection', '植物保护', 'Other'],
    'basic_medicine': ['Basic Medicine', '基础医学', 'Other'],
    'clinical_medicine': ['Clinical Medicine', '临床医学', 'Other'],
    'urban_and_rural_planner': ['Urban and Rural Planner', '注册城乡规划师', 'Other'],
    'accountant': ['Accountant', '注册会计师', 'Other'],
    'fire_engineer': ['Fire Engineer', '注册消防工程师', 'Other'],
    'environmental_impact_assessment_engineer': ['Environmental Impact Assessment Engineer', '环境影响评价工程师', 'Other'],
    'tax_accountant': ['Tax Accountant', '税务师', 'Other'],
    'physician': ['Physician', '医师资格', 'Other'],
}
ceval_all_sets = list(ceval_subject_mapping.keys())

prompt = "以下是中国关于{subject}考试的单项选择题，请选出其中的正确答案。\n{question}\nA. {A}\nB. {B}\nC. {C}\nD. {D}\n答案: "

dev_data_map = dict()

for tf in dev_files:
    t_sub = tf.replace("_dev.csv", "")
    t_sub_name = ceval_subject_mapping[t_sub][1]

    dev_data = pandas.read_csv(os.path.join(base_dir, "dev", tf))

    samples = list()
    for td in dev_data.iterrows():
        samples.append(prompt.format(
            subject=t_sub_name,
            question=td[1]['question'],
            A=td[1]['A'],
            B=td[1]['B'],
            C=td[1]['C'],
            D=td[1]['D'],
        ) + td[1]['answer'])
    dev_data_map[t_sub] = samples

data_list = list()

for tf in val_files:
    t_sub = tf.replace("_val.csv", "")
    t_sub_name = ceval_subject_mapping[t_sub][1]
    val_data = pandas.read_csv(os.path.join(base_dir, "val", tf))

    for td in val_data.iterrows():
        t_query = "\n".join(dev_data_map[t_sub][0: 3]) + "\n" + prompt.format(
            subject=t_sub_name,
            question=td[1]['question'],
            A=td[1]['A'],
            B=td[1]['B'],
            C=td[1]['C'],
            D=td[1]['D'],
        )

        md = {
            "id": t_sub + "_" + str(td[1]['id']).zfill(8),
            "query": t_query,
            "answer": td[1]['answer'],
            "type_list": ceval_subject_mapping[t_sub]
        }

        data_list.append(md)

fw = open(f"./eval_data/ceval_3shots_val_{len(data_list)}.json", mode="w", encoding="utf-8")
json.dump(data_list, fw, ensure_ascii=False, indent=2)
fw.close()
