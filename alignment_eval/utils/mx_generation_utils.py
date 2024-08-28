# coding: utf-8
# @author: kaimin
# @time: 2023-10-17 11:07
import re
from typing import List, Tuple

from transformers import PreTrainedTokenizer

"""

统一到（query, content）的格式

拼接     88
系统     89
用户     90
助手     91
代理     92

"""


def is_blank(p_str: str):
    if p_str is None:
        return True
    if len(p_str) == 0:
        return True

    for tc in p_str:
        if not tc.isspace():
            return False

    return True


def get_prompt(sample):
    add_sign = "\n"

    if not (is_blank(sample.get('instruction')) and is_blank(sample.get('input'))):
        if is_blank(sample.get('input')):
            t_input = ""
        else:
            t_input = add_sign + sample['input']

        if is_blank(sample.get('instruction')):
            t_instruction = ""
        else:
            t_instruction = sample['instruction']
        return t_instruction + t_input

    return None


ROLE_STR_MAP = {
    "\n\n【--系统--】：\n\n": "system",
    "\n\n【--用户--】：\n\n": "user",
    "\n\n【--助手--】：\n\n": "assistant",
    "\n\n【--代理--】：\n\n": "observer",
}
SPLIT_PATTERN_STR = "(" + "|".join(ROLE_STR_MAP.keys()) + ")"
SPLIT_PATTERN = re.compile(SPLIT_PATTERN_STR)


def build_qa_list(p_prompt):
    # 按照分割符切分
    parts = SPLIT_PATTERN.split(p_prompt)
    ret_list = []
    i = 0

    # 遍历并校验数据，成对而且包含内容
    while i < len(parts):
        if parts[i] in ROLE_STR_MAP and i + 1 < len(parts) and not is_blank(parts[i + 1]):
            ret_list.append({"role": ROLE_STR_MAP.get(parts[i]), "content": parts[i + 1]})
            i += 2
        else:
            i += 1

    return ret_list


def check_assistant_start(
        p_index: int,
        p_input_ids: List[int],
        tokenizer: PreTrainedTokenizer,
        start_char: str = ":",
        assistant_word: str = "助手",
        new_line_char: str = "\n"
):
    """
    校验当前是不是助手角色的开始
    """
    start_token_id = tokenizer._convert_token_to_id(start_char)
    if start_token_id != p_input_ids[p_index]:
        return False
    if p_index - 3 < 0:
        return False
    assistant_token_id = tokenizer._convert_token_to_id(assistant_word)
    if p_input_ids[p_index - 1] != assistant_token_id:
        return False
    new_line_token_id = tokenizer._convert_token_to_id(new_line_char)
    if p_input_ids[p_index - 2] != new_line_token_id:
        return False
    if p_input_ids[p_index - 3] != new_line_token_id:
        return False
    return True


def build_inputs(
        messages: List[Tuple[str, str]],
        tokenizer: PreTrainedTokenizer,
        system_content: str = "",
        bos_token: int = 1,
        eos_token: int = 2,
        concat_token: int = 88,
        system_role: str = "\n\n系统:",
        user_role: str = "\n\n用户:",
        assistant_role: str = "\n\n助手:",
        observer_role: str = "\n\n代理:",
        max_input_tokens: int = -1
):
    """
    chat调用的
    messages: (role, content)
    """

    if messages is None or len(messages) == 0:
        return []

    def _tokenize_str(role, content):
        if role == "system":
            return [bos_token] + tokenizer.encode(system_role) + tokenizer.encode(content) + [eos_token, concat_token]
        elif role == "user":
            return [bos_token] + tokenizer.encode(user_role) + tokenizer.encode(content) + [eos_token, concat_token]
        elif role == "assistant":
            return [bos_token] + tokenizer.encode(assistant_role) + tokenizer.encode(content) + [eos_token, concat_token]
        elif role == "observer":
            return [bos_token] + tokenizer.encode(observer_role) + tokenizer.encode(content) + [eos_token, concat_token]
        else:
            raise ValueError(f"message role not supported yet: {role}")

    context_tokens = []
    system_tokens = []
    if not is_blank(system_content):
        system_tokens = _tokenize_str("system", system_content)

    for t_role, t_message in reversed(messages):
        current_tokens = _tokenize_str(t_role, t_message)
        if 0 < max_input_tokens < len(system_tokens + context_tokens + current_tokens):
            break
        context_tokens = current_tokens + context_tokens

    # 拼接system tokens在头上
    context_tokens = system_tokens + context_tokens

    # 助手回答的开始token
    context_tokens += [bos_token] + tokenizer.encode(assistant_role)

    return context_tokens


def build_result(
        result: str,
        tokenizer: PreTrainedTokenizer,
        eos_token: int = 2,
):
    return tokenizer.encode(result) + [eos_token]


def check_role_start(
        p_index: int,
        p_input_ids: List[int],
        tokenizer: PreTrainedTokenizer,
        start_char: str = ":",
        system_word: str = "系统",
        user_word: str = "用户",
        assistant_word: str = "助手",
        observer_word: str = "代理",
        new_line_char: str = "\n"
):
    """
    校验当前是不是助手角色的开始
    """

    start_token_id = tokenizer._convert_token_to_id(start_char)
    if start_token_id != p_input_ids[p_index]:
        return None
    if p_index - 3 < 0:
        return None
    role_token_ids = [tokenizer._convert_token_to_id(system_word), tokenizer._convert_token_to_id(user_word),
                      tokenizer._convert_token_to_id(assistant_word), tokenizer._convert_token_to_id(observer_word)]
    if p_input_ids[p_index - 1] not in role_token_ids:
        return None
    new_line_token_id = tokenizer._convert_token_to_id(new_line_char)
    if p_input_ids[p_index - 2] != new_line_token_id:
        return None
    if p_input_ids[p_index - 3] != new_line_token_id:
        return None

    if p_input_ids[p_index - 1] == tokenizer._convert_token_to_id(system_word):
        return "system"
    elif p_input_ids[p_index - 1] == tokenizer._convert_token_to_id(user_word):
        return "user"
    elif p_input_ids[p_index - 1] == tokenizer._convert_token_to_id(assistant_word):
        return "assistant"
    elif p_input_ids[p_index - 1] == tokenizer._convert_token_to_id(observer_word):
        return "observer"
    else:
        return None


def check_role_start_v2(
        p_index: int,
        p_input_ids: List[int],
        tokenizer: PreTrainedTokenizer,
        start_char: str = ":",
        system_word: str = "系统",
        user_word: str = "用户",
        assistant_word: str = "助手",
        observer_word: str = "代理",
        new_line_char: str = "\n"
):
    """
    校验当前是不是助手角色的开始
    """

    start_token_id = tokenizer._convert_token_to_id(start_char)
    if start_token_id != p_input_ids[p_index]:
        return None
    if p_index - 2 < 0:
        return None
    role_token_ids = [tokenizer._convert_token_to_id(system_word), tokenizer._convert_token_to_id(user_word),
                      tokenizer._convert_token_to_id(assistant_word), tokenizer._convert_token_to_id(observer_word)]
    if p_input_ids[p_index - 1] not in role_token_ids:
        return None
    new_line_token_id = tokenizer._convert_token_to_id(new_line_char + new_line_char)
    if p_input_ids[p_index - 2] != new_line_token_id:
        return None

    if p_input_ids[p_index - 1] == tokenizer._convert_token_to_id(system_word):
        return "system"
    elif p_input_ids[p_index - 1] == tokenizer._convert_token_to_id(user_word):
        return "user"
    elif p_input_ids[p_index - 1] == tokenizer._convert_token_to_id(assistant_word):
        return "assistant"
    elif p_input_ids[p_index - 1] == tokenizer._convert_token_to_id(observer_word):
        return "observer"
    else:
        return None