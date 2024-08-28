# coding: utf-8
# @author: kaimin
# @time: 2024-01-03 19:30
import argparse
import json
import os.path

import markdown2

from alignment_eval.utils.mx_generation_utils import is_blank


def trans2html(p_json_data, p_output_file, p_model1_name, p_model2_name):
    # 解析JSON字符串
    data_list = p_json_data

    html_header = """<html>
<head><title>Q&A Table</title>
    <meta charset="utf-8">
    <style>
        td {vertical-align: top; border: 1px solid black; max-width: 900px;}
        code {background-color: #FFE4E1; padding: 2px 4px; border-radius: 4px; font-family: monospace;}
        thead {border: 2px solid black;}
        tbody {border: 2px solid black;}
    </style>
</head>
    """

    # 构建HTML表格的开头
    html_content = html_header + '<body>'
    html_content += '<table border="1">'
    # 模型1 模型2名字
    html_content += '<tr><td>' + p_model1_name + '</td>'
    html_content += '<td>' + p_model2_name + '</td></tr>'

    # 遍历数据并构建表格行
    for item in data_list:
        t_id = item['id']
        question_html = markdown2.markdown(item['query'].replace('\n', '<br>'), extras=["fenced-code-blocks", "tables"])
        answer1_html = markdown2.markdown(item['output1'], extras=["fenced-code-blocks", "tables"])
        answer2_html = markdown2.markdown(item['output2'], extras=["fenced-code-blocks", "tables"])

        # 将问题添加到表格的一行中
        html_content += '<tr><td colspan="2">' + t_id + '</td></tr>'
        if not is_blank(item.get('desc')):
            html_content += '<tr><td colspan="2">' + item["desc"] + '</td></tr>'
        html_content += '<tr><td colspan="2">' + question_html + '</td></tr>'

        if not is_blank(item.get('score_1')) and not is_blank(item.get('score_2')):
            html_content += '<tr>'
            html_content += '<td style="width: 50%;">' + item['score_1'] + '</td>'
            html_content += '<td style="width: 50%;">' + item['score_2'] + '</td>'
            html_content += '</tr>'

        # 将答案添加到表格的下一行中，分成两个单元格
        html_content += '<tr>'
        html_content += '<td style="width: 50%;">' + answer1_html + '</td>'
        html_content += '<td style="width: 50%;">' + answer2_html + '</td>'
        html_content += '</tr>'

        # 结束HTML表格
    html_content += '</table>'
    html_content += '</body></html>'

    # 输出结果，或者将其写入到HTML文件中
    with open(p_output_file, 'w', encoding="utf-8") as file:
        file.write(html_content)


def build_json_data(p_file_1, p_file_2):
    ROLE_STR_MAP = {
        "system": "\n\n【--系统--】：\n\n",
        "user": "\n\n【--用户--】：\n\n",
        "assistant": "\n\n【--助手--】：\n\n",
        "observer": "\n\n【--代理--】：\n\n",
    }

    def _build_messages(p_message_list, p_system_content):
        ret_str = ROLE_STR_MAP['system'] + p_system_content
        for tm in p_message_list:
            ret_str += ROLE_STR_MAP[tm['role']] + tm['content']
        return ret_str

    with open(p_file_1, 'r', encoding="utf-8") as file:
        data_1 = json.load(file)

    with open(p_file_2, 'r', encoding="utf-8") as file:
        data_2 = json.load(file)

    data_map = dict()
    for td in data_1:
        if not is_blank(td.get('category')):
            md = {
                "id": td['trace_id'],
                "desc": f"类型: {td['category']}",
                "query": _build_messages(td['messages'], td['system_content']),
                "score_1": f"score: {td['score'][0]}<br>{td['gpt_score_result'][0]}",
                "output1": td['response'],
                "output2": "",
            }
        else:
            md = {
                "id": td['trace_id'],
                "query": _build_messages(td['messages'], td['system_content']),
                "output1": td['response'],
                "output2": "",
            }
        data_map[td['trace_id']] = md

    for td in data_2:
        if td['trace_id'] in data_map:
            data_map[td['trace_id']]['output2'] = td['response']
            data_map[td['trace_id']]['score_2'] = f"score: {td['score'][0]}<br>{td['gpt_score_result'][0]}"

    return list(data_map.values())


def build_json_lines_data(p_file_1, p_file_2):
    ROLE_STR_MAP = {
        "system": "\n\n【--系统--】：\n\n",
        "user": "\n\n【--用户--】：\n\n",
        "assistant": "\n\n【--助手--】：\n\n",
        "observer": "\n\n【--代理--】：\n\n",
    }

    def _build_messages(p_message_list, p_system_content):
        ret_str = ROLE_STR_MAP['system'] + p_system_content
        for tm in p_message_list:
            ret_str += ROLE_STR_MAP[tm['role']] + tm['content']
        return ret_str

    with open(p_file_1, 'r', encoding="utf-8") as file:
        data_1 = json.load(file)

    with open(p_file_2, 'r', encoding="utf-8") as file:
        data_2 = file.readlines()

    data_map = dict()
    for td in data_1:
        # td = json.loads(td)
        if not is_blank(td.get('category')):
            if not is_blank(td.get('score')):
                md = {
                    "id": td['trace_id'],
                    "desc": f"类型: {td['category']}",
                    "query": _build_messages(td['messages'], td['system_content']),
                    "score_1": f"score: {td['score'][0]}<br>{td['gpt_score_result'][0]}",
                    "output1": td['response'],
                    "output2": "",
                }
            else:
                md = {
                    "id": td['trace_id'],
                    "desc": f"类型: {td['category']}",
                    "query": _build_messages(td['messages'], td['system_content']),
                    "output1": td['response'],
                    "output2": "",
                }
        else:
            md = {
                "id": td['trace_id'],
                "query": _build_messages(td['messages'], td['system_content']),
                "output1": td['response'],
                "output2": "",
            }
        data_map[td['trace_id']] = md

    for td in data_2:
        td = json.loads(td)
        if td['trace_id'] in data_map:
            data_map[td['trace_id']]['output2'] = td['response']
            if not is_blank(td.get('score')):
                data_map[td['trace_id']]['score_2'] = f"score: {td['score'][0]}<br>{td['gpt_score_result'][0]}"

    return list(data_map.values())


def add_score_data(p_data, p_file_1, p_file_2, p_model_1, p_model_2):
    with open(p_file_1, 'r', encoding="utf-8") as file:
        data_1 = json.load(file)

    with open(p_file_2, 'r', encoding="utf-8") as file:
        data_2 = json.load(file)

    data_map_1 = dict()
    data_map_2 = dict()
    for td in data_1:
        data_map_1[td['id']] = td['score']
    for td in data_2:
        data_map_2[td['id']] = td['score']

    model_1_win = 0
    model_2_win = 0
    draw_count = 0

    for td in p_data:
        if td['id'] in data_map_1 and td['id'] in data_map_2:
            if data_map_1[td['id']] > data_map_2[td['id']]:
                model_1_win += 1
            elif data_map_1[td['id']] < data_map_2[td['id']]:
                model_2_win += 1
            else:
                draw_count += 1
            td["score_1"] = str(data_map_1[td['id']])
            td["score_2"] = str(data_map_2[td['id']])

    print(f"{p_model_1} win {model_1_win / (model_1_win + model_2_win + draw_count)}, win count {model_1_win}")
    print(f"{p_model_2} win {model_2_win / (model_1_win + model_2_win + draw_count)}, win count {model_2_win}")
    print(f"draw {draw_count / (model_1_win + model_2_win + draw_count)}, draw count {draw_count}")


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--output1", help="对比输出1")
    # parser.add_argument("--output2", help="对比输出2")
    # parser.add_argument("--score_output1", default="", help="对应分数结果输出1")
    # parser.add_argument("--score_output2", default="", help="对应分数结果输出2")
    # parser.add_argument("--model_name1", help="模型名/版本1")
    # parser.add_argument("--model_name2", help="模型名/版本2")
    # parser.add_argument("--html_output_path", help="输出结果文件(html)")
    # args = parser.parse_args()
    #
    # json_data = build_json_lines_data(args.output1, args.output2)
    #
    # if not is_blank(args.score_output1) and not is_blank(args.score_output2):
    #     if os.path.exists(args.score_output1) and os.path.exists(args.score_output2):
    #         add_score_data(json_data, args.score_output1, args.score_output2, args.model_name1, args.model_name2)
    #
    # trans2html(json_data, args.html_output_path, args.model_name1, args.model_name2)
    # print(f"finish model compare {args.model_name1} & {args.model_name2}, results {args.html_output_path}")

    output1 = "D:/em_im_files/file/2024-06/iter_0002262_std.json"
    output2 = "E:/alg_eval/llm-alignment-eval/tmp/busEval/mx66b_240528/mx66b_240528_results.jsonl"
    model_name1 = "vllm_0528"
    model_name2 = "trt_0528"
    html_output_path = f"{model_name1}_vs_{model_name2}.html"

    json_data = build_json_lines_data(output1, output2)
    json_data = list(sorted(json_data, key=lambda x: x['desc']))

    trans2html(json_data, html_output_path, model_name1, model_name2)
