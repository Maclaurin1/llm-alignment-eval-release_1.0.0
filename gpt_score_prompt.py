import json
import jsonlines

from alignment_eval.models import GPTApi, GptIntApi
from alignment_eval.em_eval.gpt_score_eval import GPTScoreEval

file_path = r'D:\eval\MT-Eval-main\inference_outputs\32k_base_sub\32k_base_sub_results.jsonl'

f = open(file_path, 'r', encoding='UTF-8')
# test_data = json.load(f)
test_data = []
for sample in jsonlines.Reader(f):
    test_data.append(sample)


model_url = 'http://61.129.116.136:8651/chatCompletion'
user_token = '240151_aN8z2gtiudKoinIfvcwd'
model = GptIntApi(model_url, token=user_token)

gpt_eval = GPTScoreEval(model)
gpt_eval.score(
    test_data,
    r'D:\eval\MT-Eval-main\inference_outputs\32k_base_sub\32k_base_sub_score.jsonl'
)