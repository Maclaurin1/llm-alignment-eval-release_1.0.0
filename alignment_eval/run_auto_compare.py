# coding: utf-8
# @author: kaimin
# @time: 2024-05-15 08:56
import argparse
import os.path

from alignment_eval.results_compare.compare_manager import CompareManager


def do_compare(p_out_dir1, p_out_dir2, p_model_name1, p_model_name2, p_qw_url, p_qw_token):
    cm = CompareManager(p_out_dir1, p_out_dir2, p_model_name1, p_model_name2, p_qw_url, p_qw_token)
    res = cm.gen_compare_result()

    # 结果暂时是写在p_out_dir1里面
    fw = open(os.path.join(p_out_dir1, f"{p_model_name1}_vs_{p_model_name2}.md"), mode="w", encoding="utf-8")
    fw.write(res)
    fw.close()


DF_OUT1 = r"D:\eval\llm-alignment-eval-release_1.0.0\llm-alignment-eval-release_1.0.0\output\wzc_192_MT"
DF_OUT2 = r"D:\eval\llm-alignment-eval-release_1.0.0\llm-alignment-eval-release_1.0.0\output\zhaowen"
DF_MODEL1 = "wzc_192_MT"
DF_MODEL2 = "zhaowen"

DF_QWEN_URL = 'http://1411998742277274.cn-wulanchabu.pai-eas.aliyuncs.com/api/predict/rlhf_qwen_2_72b_clone/v1/chat/completions'
DF_QWEN_TOKEN = 'OGViNTcxOTNiZDUwNzYxM2RjMzJiZDA1ZThlMTU1ZTc0YmEzODNlNg=='

if __name__ == '__main__':
    # 与生成的模型名一致，需要按规则匹配路径的
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir1", default=DF_OUT1, help="数据路径1")
    parser.add_argument("--out_dir2", default=DF_OUT2, help="输出路径2")
    parser.add_argument("--model_name1", default=DF_MODEL1, help="模型名1")
    parser.add_argument("--model_name2", default=DF_MODEL2, help="模型名2")
    parser.add_argument("--qwen_url", default=DF_QWEN_URL, help="千问url")
    parser.add_argument("--qwen_token", default=DF_QWEN_TOKEN, help="千问token")
    args = parser.parse_args()

    do_compare(args.out_dir1, args.out_dir2, args.model_name1, args.model_name2, args.qwen_url, args.qwen_token)
    print(f"finish score out dir {args.out_dir1}")