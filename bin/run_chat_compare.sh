#!/pkl/bash

BASE_DIR="$( cd "$(dirname "$0")" ; pwd -P )/.."
export PYTHONPATH=${BASE_DIR}:${PYTHONPATH}

DATA_PATH=${BASE_DIR}/compare_data/chat_base_tests_240130.json

MODEL_NAME_1=ppo_66b_240131
MODEL_URL_1=http://10.205.92.13:30666/worker_generate

MODEL_NAME_2=summary_66b_240126
MODEL_URL_2=http://10.205.92.11:31009/worker_generate

TK_PATH=/opt/data1/kaimin/tokenizer_hf_em_v1
LOG_DIR=${BASE_DIR}/chat_logs
OUTPUT_DIR=${BASE_DIR}/chat_outputs

mkdir -p ${LOG_DIR}
mkdir -p ${OUTPUT_DIR}

LOG_PATH_1=${LOG_DIR}/${MODEL_NAME_1}_$(date "+%Y%m%d").log
LOG_PATH_2=${LOG_DIR}/${MODEL_NAME_2}_$(date "+%Y%m%d").log

# batch generate
python ${BASE_DIR}/alignment_eval/run_compare.py \
  --output_dir ${OUTPUT_DIR} \
  --data_path ${DATA_PATH} \
  --model_name ${MODEL_NAME_1} \
  --model_url ${MODEL_URL_1} &> ${LOG_PATH_1} &

python ${BASE_DIR}/alignment_eval/run_compare.py \
  --output_dir ${OUTPUT_DIR} \
  --data_path ${DATA_PATH} \
  --model_name ${MODEL_NAME_2} \
  --model_url ${MODEL_URL_2} &> ${LOG_PATH_2} &

echo generating...

# waiting
wait

mkdir -p ${OUTPUT_DIR}/html_compare_results

# build rm pkl file, then run rm score with ali-dlc
# if add sys
#python ${BASE_DIR}/alignment_eval/trans_rm_pkl.py \
#  --data_path ${OUTPUT_DIR}/${MODEL_NAME_1}/${MODEL_NAME_1}_results.jsonl \
#  --pkl_path ${OUTPUT_DIR}/${MODEL_NAME_1}/${MODEL_NAME_1}_rm.pkl \
#  --tokenizer ${TK_PATH} \
#  --add_system
#
#python ${BASE_DIR}/alignment_eval/trans_rm_pkl.py \
#  --data_path ${OUTPUT_DIR}/${MODEL_NAME_2}/${MODEL_NAME_2}_results.jsonl \
#  --pkl_path ${OUTPUT_DIR}/${MODEL_NAME_2}/${MODEL_NAME_2}_rm.pkl \
#  --tokenizer ${TK_PATH} \
#  --add_system

# if not add sys
python ${BASE_DIR}/alignment_eval/trans_rm_pkl.py \
  --data_path ${OUTPUT_DIR}/${MODEL_NAME_1}/${MODEL_NAME_1}_results.jsonl \
  --pkl_path ${OUTPUT_DIR}/${MODEL_NAME_1}/${MODEL_NAME_1}_rm.pkl \
  --tokenizer ${TK_PATH}

python ${BASE_DIR}/alignment_eval/trans_rm_pkl.py \
  --data_path ${OUTPUT_DIR}/${MODEL_NAME_2}/${MODEL_NAME_2}_results.jsonl \
  --pkl_path ${OUTPUT_DIR}/${MODEL_NAME_2}/${MODEL_NAME_2}_rm.pkl \
  --tokenizer ${TK_PATH}

# summarize results and generate html compare file
python ${BASE_DIR}/alignment_eval/html_convert.py \
  --output1 ${OUTPUT_DIR}/${MODEL_NAME_1}/${MODEL_NAME_1}_results.jsonl \
  --output2 ${OUTPUT_DIR}/${MODEL_NAME_2}/${MODEL_NAME_2}_results.jsonl \
  --model_name1 ${MODEL_NAME_1} \
  --model_name2 ${MODEL_NAME_2} \
  --score_output1 ${OUTPUT_DIR}/${MODEL_NAME_1}/${MODEL_NAME_1}_rm.json \
  --score_output2 ${OUTPUT_DIR}/${MODEL_NAME_2}/${MODEL_NAME_2}_rm.json \
  --html_output_path ${OUTPUT_DIR}/html_compare_results/${MODEL_NAME_1}_vs_${MODEL_NAME_2}.html
