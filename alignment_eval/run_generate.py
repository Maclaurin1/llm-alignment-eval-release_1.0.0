# coding: utf-8
# @author: kaimin
# @time: 2024-01-22 17:00

"""
采用 worker_generate api 评估模型
输入两个接口和测试文件
输出对比的html
"""
import argparse

from alignment_eval.manager import GenerateManager
from alignment_eval.models import *


def build_model(p_model_type, p_model_url, p_token, p_tokenizer_path):
    ret_model = None

    if p_model_type == "mx":
        ret_model = MxApi(model=p_model_url, workers=4, retry=2)
    elif p_model_type == "trt":
        ret_model = MxTrtApi(model=p_model_url, tokenizer_path=p_tokenizer_path, token=p_token, workers=4, retry=2)
    elif p_model_type == "qwtrt":
        ret_model = QwenTrtApi(model=p_model_url, tokenizer_path=p_tokenizer_path, token=p_token, workers=4, retry=2)
    elif p_model_type == "qwen":
        ret_model = QwenApi(model=p_model_url, token=p_token, workers=4, retry=2)
    elif p_model_type == 'gpt':
        ret_model = GPTApi(model=p_model_url, token=p_token, retry=2)
    elif p_model_type == 'glm':
        # p_model_url glm 情况下可选只有 glm-4 和 glm-3-turbo
        if p_model_url in ['glm-4', 'glm-3-turbo']:
            ret_model = GLMApi(model=p_model_url, token=p_token, workers=4, retry=2)
    elif p_model_type == 'ms':
        ret_model = MsApi(model=p_model_url, token=p_token, workers=4, retry=2)

    return ret_model


DF_OUT_DIR = r"E:\eastmoney\llm-alignment-eval-release_1.0.0\output"
DF_DATA_PATH = r"E:\eastmoney\llm-alignment-eval-release_1.0.0\eval_data\ZHIFEval.json"
DF_TOKENIZER = r"D:\eval\llm-alignment-eval-release_1.0.0\llm-alignment-eval-release_1.0.0\tokenizer\qwen_shuffle_tokenizer"
DF_MODEL_NAME = "rlhf_qwen2_ZH"
DF_MODEL_TYPE = "qwen"

DF_URL = "http://1411998742277274.cn-wulanchabu.pai-eas.aliyuncs.com/api/predict/rlhf_qwen_2_72b_clone/v1/chat/completions"
DF_TOKEN = "OGViNTcxOTNiZDUwNzYxM2RjMzJiZDA1ZThlMTU1ZTc0YmEzODNlNg=="

# DF_URL = "http://1411998742277274.cn-wulanchabu.pai-eas.aliyuncs.com/api/predict/qwen_bladellm_test/v1/chat/completions"
# DF_TOKEN = "=="

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", default=DF_OUT_DIR, help="输出路径")
    parser.add_argument("--data_path", default=DF_DATA_PATH, help="数据路径")
    parser.add_argument("--tokenizer_path", default=DF_TOKENIZER, help="分词器路径")
    parser.add_argument("--model_name", default=DF_MODEL_NAME, help="模型名/版本")
    parser.add_argument('--model_type', default=DF_MODEL_TYPE, choices=['mx', 'gpt', 'glm', 'ms', 'trt', 'qwen', "qwtrt"], help='Model type mx(miaoxiang), gpt, glm, ms(moonshot).')
    parser.add_argument("--model_url", default=DF_URL, help="模型调用接口url，或者GLM情况的模型名")
    parser.add_argument("--model_token", default=DF_TOKEN, help="模型调用接口url的token")
    args = parser.parse_args()

    m_model = build_model(p_model_type=args.model_type, p_model_url=args.model_url, p_token=args.model_token, p_tokenizer_path=args.tokenizer_path)
    tm = GenerateManager(
        p_output_dir=args.output_dir,
        p_data_path=args.data_path,
        p_model_name=args.model_name,
        p_model=m_model
    )

    tm.do_generate()
    print(f"finish eval {args.data_path}, model {args.model_name}, results path {args.output_dir}")