#!/bin/bash

BASE_DIR=/D/eval/llm-alignment-eval-release_1.0.0/llm-alignment-eval-release_1.0.0
export PYTHONPATH=${BASE_DIR}:${PYTHONPATH}

MODEL_NAME=mx
MODEL_URL=XXX
MODEL_TYPE=gpt
TOKEN=XXX
LOG_DIR=${BASE_DIR}logs
mkdir -p ${LOG_DIR}

DATA_PATH=${BASE_DIR}/eval_data/ZhMtBench_mx_api.json
OUTPUT_DIR=${BASE_DIR}/ZhMtBench

mkdir -p ${OUTPUT_DIR}

# batch generate
python ${BASE_DIR}/alignment_eval/run_generate.py \
  --output_dir ${OUTPUT_DIR} \
  --data_path ${DATA_PATH} \
  --model_name ${MODEL_NAME} \
  --model_type ${MODEL_TYPE} \
  --model_url ${MODEL_URL} \
  --model_token ${TOKEN}

DATA_PATH=${BASE_DIR}/eval_data/ZhIFEval_mx_api.json
OUTPUT_DIR=${BASE_DIR}/ZhIFEval
mkdir -p ${OUTPUT_DIR}

# batch generate
python ${BASE_DIR}/alignment_eval/run_generate.py \
  --output_dir ${OUTPUT_DIR} \
  --data_path ${DATA_PATH} \
  --model_name ${MODEL_NAME} \
  --model_type ${MODEL_TYPE} \
  --model_url ${MODEL_URL} \
  --model_token ${TOKEN}

DATA_PATH=${BASE_DIR}/eval_data/MtBench_mx_api.json
OUTPUT_DIR=${BASE_DIR}/MtBench
mkdir -p ${OUTPUT_DIR}

# batch generate
python ${BASE_DIR}/alignment_eval/run_generate.py \
  --output_dir ${OUTPUT_DIR} \
  --data_path ${DATA_PATH} \
  --model_name ${MODEL_NAME} \
  --model_type ${MODEL_TYPE} \
  --model_url ${MODEL_URL} \
  --model_token ${TOKEN}

DATA_PATH=${BASE_DIR}/eval_data/IFEval_mx_api.json
OUTPUT_DIR=${BASE_DIR}/IFEval
mkdir -p ${OUTPUT_DIR}

# batch generate
python ${BASE_DIR}/alignment_eval/run_generate.py \
  --output_dir ${OUTPUT_DIR} \
  --data_path ${DATA_PATH} \
  --model_name ${MODEL_NAME} \
  --model_type ${MODEL_TYPE} \
  --model_url ${MODEL_URL} \
  --model_token ${TOKEN}

