# llm-alignment-eval

## 评估任务

选择题：ceval，mmlu，enfin，abcEval

匹配题：GSM8K，RAIFB，IF，zh-IF，大海捞针（仅32K测）

主观题：mtbench，zh-mtbench，AlignBench

## 评估形式

1. 数据预先组合，批量跑生成；
2. api调用生成；
3. 转token自动化评估，下载后东财环境解码；
4. 统一算分；

## 评估数据
```json
{
  "trace_id": "",
  "system_content": "你的名字是妙想，你是东方财富公司自主研发的金融行业大语言模型，来帮助用户获取有用信息。",
  "eval_set_name": "",
  "category": "",
  "subcategory": "",
  "messages": [],
  "top_p": 0.85,
  "top_k": 5,
  "temperature": 0.7,
  "max_new_tokens": 800,
  "options": [],
  "reference": [],
  "instruction_id_list": [],
  "kwargs": [],
  "gpt_score_prompt": [
    ""
  ],
  "gpt_score_result": [
    ""
  ]
}
```

## 跑数据生成response
[run_generate.py](alignment_eval%2Frun_generate.py)

妙想建议主要采用，trt类型加载tokenizer之后直接调用eas的trtllm推理服务。下面是一个样例，注意url配的是一个流式的接口。

```bash

#!/bin/bash

BASE_DIR="$( cd "$(dirname "$0")" ; pwd -P )/.."
export PYTHONPATH=${BASE_DIR}:${PYTHONPATH}

MODEL_NAME=mx66b_32k_240511
MODEL_URL=http://1411998742277274.cn-wulanchabu.pai-eas.aliyuncs.com/api/predict/mx66b_32k/v2/models/tensorrt_llm_bls/generate_stream
MODEL_TYPE=trt
TOKEN= ...
TOKENIZER_PATH=/opt/data1/kaimin/tokenizer_hf_em_v1/

LOG_DIR=${BASE_DIR}logs
DATA_DIR=/opt/data1/alignment_eval_data
RES_DIR=${BASE_DIR}/results
mkdir -p ${LOG_DIR}


# AlignBench batch generate
DATA_PATH=${DATA_DIR}/all_alignment_eval_12872.json
OUTPUT_DIR=${RES_DIR}/ALL_ALIGNMENT
mkdir -p ${OUTPUT_DIR}
echo ${OUTPUT_DIR}

python ${BASE_DIR}/alignment_eval/run_generate.py \
  --output_dir ${OUTPUT_DIR} \
  --data_path ${DATA_PATH} \
  --model_name ${MODEL_NAME} \
  --model_type ${MODEL_TYPE} \
  --model_url ${MODEL_URL} \
  --model_token ${TOKEN} \
  --tokenizer_path ${TOKENIZER_PATH}

```

## 跑评分

除了AlignBench、MtBench、ZhMtBench需要用大模型评估外，下面的方法能完成其他自动的评估，可以参考默认设置参数运行。

PS. AlignBench的CSV会顺带生成的。

[run_score.py](alignment_eval%2Frun_score.py)


## 生成报告

会用千问读数据生成一份完整的评估报告，可以参考默认设置参数运行。

[run_auto_compare.py](alignment_eval%2Frun_auto_compare.py)
