# Copyright 2023 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Registry of all instructions."""
from . import instructions as instructions

_KEYWORD = 'keywords:'

_LANGUAGE = 'language:'

_LENGTH = 'length_constraints:'

_CONTENT = 'detectable_content:'

_FORMAT = 'detectable_format:'

_MULTITURN = 'multi-turn:'

_COMBINATION = 'combination:'

_STARTEND = 'startend:'

_PUNCTUATION = 'punctuation:'

INSTRUCTION_DICT = {
    _KEYWORD + 'existence': instructions.KeywordChecker,
    # _KEYWORD + 'sentence': instructions.KeySentenceChecker,
    _KEYWORD + 'frequency': instructions.KeywordFrequencyChecker,
    _KEYWORD + 'forbidden_words': instructions.ForbiddenWords,
    _KEYWORD + 'ordered_words': instructions.OrderedWords,

    _LANGUAGE + 'response_language': instructions.ResponseLanguageChecker,

    _LENGTH + 'number_sentences': instructions.NumberOfSentences,
    _LENGTH + 'number_paragraphs': instructions.ParagraphChecker,
    _LENGTH + 'number_characters': instructions.NumberOfCharacters,
    _LENGTH + 'nth_paragraph_first_word': instructions.ParagraphFirstWordCheck,

    _CONTENT + 'number_placeholders': instructions.PlaceholderChecker,
    _CONTENT + 'postscript': instructions.PostscriptChecker,
    _CONTENT + 'statement': instructions.StatementChecker,
    _CONTENT + 'tabel': instructions.TabelChecker,

    _FORMAT + 'number_bullet_lists': instructions.BulletListChecker,
    _FORMAT + 'constrained_response': instructions.ConstrainedResponseChecker,
    _FORMAT + 'number_highlighted_sections': instructions.HighlightSectionChecker,
    _FORMAT + 'multiple_sections': instructions.SectionChecker,
    _FORMAT + 'json_format': instructions.JsonFormat,
    _FORMAT + 'title': instructions.TitleChecker,

    _FORMAT + "order_list_1": instructions.OrderList1Checker,
    _FORMAT + "order_list_2": instructions.OrderList2Checker,
    _FORMAT + "order_list_3": instructions.OrderList3Checker,
    _FORMAT + "sub_title_2": instructions.SubTitle2Checker,
    _FORMAT + "sub_title_3": instructions.SubTitle3Checker,
    _FORMAT + "sub_script": instructions.SubScriptChecker,

    _COMBINATION + 'two_responses': instructions.TwoResponsesChecker,
    _COMBINATION + 'repeat_prompt': instructions.RepeatPromptThenAnswer,

    _PUNCTUATION + 'no_comma': instructions.CommaChecker,
    _PUNCTUATION + 'no_period': instructions.PeriodChecker,

    _STARTEND + 'quotation': instructions.QuotationChecker,
    _STARTEND + 'start_checker': instructions.StartChecker,
    _STARTEND + 'end_checker': instructions.EndChecker,
}

INSTRUCTION_CONFLICTS = {
    _KEYWORD + 'existence': {_KEYWORD + 'existence'},
    _KEYWORD + 'sentence': {_KEYWORD + 'sentence'},
    _KEYWORD + 'frequency': {_KEYWORD + 'frequency'},
    _KEYWORD + 'forbidden_words': {_KEYWORD + 'forbidden_words'},
    _KEYWORD + 'ordered_words': {
        _KEYWORD + 'existence',
        _KEYWORD + 'forbidden_words',
        _KEYWORD + 'ordered_words'
    },

    _LANGUAGE + 'response_language': {
        _LANGUAGE + 'response_language',
        _FORMAT + 'multiple_sections',
        _FORMAT + 'constrained_response',
        _FORMAT + 'title',
        _KEYWORD + 'existence',
        _KEYWORD + 'sentence',
        _KEYWORD + 'frequency',
        _KEYWORD + 'forbidden_words',
        _STARTEND + 'start_checker',
        _STARTEND + 'end_checker',
    },

    _LENGTH + 'number_sentences': {_LENGTH + 'number_sentences'},
    _LENGTH + 'number_paragraphs': {
        _LENGTH + 'number_paragraphs',
        _LENGTH + 'nth_paragraph_first_word',
        _LENGTH + 'number_sentences',
    },
    _LENGTH + 'number_characters': {_LENGTH + 'number_characters'},
    _LENGTH + 'nth_paragraph_first_word': {
        _LENGTH + 'nth_paragraph_first_word',
        _LENGTH + 'number_paragraphs',
        _LENGTH + 'number_sentences',
    },

    _CONTENT + 'number_placeholders': {_CONTENT + 'number_placeholders'},
    _CONTENT + 'postscript': {_CONTENT + 'postscript'},
    _CONTENT + 'statement': {_CONTENT + 'statement', _STARTEND + 'end_checker'},
    _CONTENT + 'tabel': {_CONTENT + 'tabel'},

    _FORMAT + 'number_bullet_lists': {_FORMAT + 'number_bullet_lists'},
    _FORMAT + 'constrained_response': set(INSTRUCTION_DICT.keys()),
    _FORMAT + 'number_highlighted_sections': {_FORMAT + 'number_highlighted_sections'},
    _FORMAT + 'multiple_sections': {
        _LANGUAGE + 'response_language',
        _FORMAT + 'multiple_sections',
        _FORMAT + 'number_highlighted_sections',
    },
    _FORMAT + 'json_format': set(INSTRUCTION_DICT.keys()).difference({
        _KEYWORD + 'forbidden_words',
        _KEYWORD + 'existence'}
    ),
    _FORMAT + 'title': {
        _FORMAT + 'title',
        _LANGUAGE + 'response_language',
    },
    _FORMAT + "order_list_1": {
        _FORMAT + 'title',
        _FORMAT + 'order_list_1',
        _FORMAT + 'order_list_2',
        _FORMAT + 'order_list_3',
        _FORMAT + 'sub_title',
        _FORMAT + 'number_bullet_lists',
    },
    _FORMAT + "order_list_2": {
        _FORMAT + 'title',
        _FORMAT + 'order_list_1',
        _FORMAT + 'order_list_2',
        _FORMAT + 'order_list_3',
        _FORMAT + 'sub_title',
        _FORMAT + 'number_bullet_lists',
    },
    _FORMAT + "order_list_3": {
        _FORMAT + 'title',
        _FORMAT + 'order_list_1',
        _FORMAT + 'order_list_2',
        _FORMAT + 'order_list_3',
        _FORMAT + 'sub_title',
        _FORMAT + 'number_bullet_lists',
    },
    _FORMAT + "sub_title_2": {
        _FORMAT + 'title',
        _FORMAT + 'order_list_1',
        _FORMAT + 'order_list_2',
        _FORMAT + 'order_list_3',
        _FORMAT + 'sub_title_2',
        _FORMAT + 'sub_title_3',
        _FORMAT + 'number_bullet_lists',
    },
    _FORMAT + "sub_title_3": {
        _FORMAT + 'title',
        _FORMAT + 'order_list_1',
        _FORMAT + 'order_list_2',
        _FORMAT + 'order_list_3',
        _FORMAT + 'sub_title_2',
        _FORMAT + 'sub_title_3',
        _FORMAT + 'number_bullet_lists',
    },
    _FORMAT + "sub_script": {
        _FORMAT + 'sub_script',
    },

    # _MULTITURN + "constrained_start": instructions.ConstrainedStartChecker,
    _COMBINATION + 'two_responses':
        set(INSTRUCTION_DICT.keys()).difference({
            _KEYWORD + 'forbidden_words', _KEYWORD + 'existence',
            _LANGUAGE + 'response_language', _FORMAT + 'title',
            _PUNCTUATION + 'no_comma'
        }),
    _COMBINATION + 'repeat_prompt':
        set(INSTRUCTION_DICT.keys()).difference(
            {_KEYWORD + 'existence', _FORMAT + 'title',
             _PUNCTUATION + 'no_comma'}),

    _PUNCTUATION + 'no_comma': {_PUNCTUATION + 'no_comma', _PUNCTUATION + 'no_period'},
    _PUNCTUATION + 'no_period': {_PUNCTUATION + 'no_comma', _PUNCTUATION + 'no_period'},

    _STARTEND + 'end_checker': {_STARTEND + 'end_checker', _CONTENT + 'statement', },
    _STARTEND + 'start_checker': {_STARTEND + 'start_checker'},
    _STARTEND + 'quotation': {_STARTEND + 'quotation', _FORMAT + 'title'},
}


def conflict_make(conflicts):
    """Makes sure if A conflicts with B, B will conflict with A.

    Args:
      conflicts: Dictionary of potential conflicts where key is instruction id
        and value is set of instruction ids that it conflicts with.

    Returns:
      Revised version of the dictionary. All instructions conflict with
      themselves. If A conflicts with B, B will conflict with A.
    """
    for key in conflicts:
        for k in conflicts[key]:
            conflicts[k].add(key)
        conflicts[key].add(key)
    return conflicts
