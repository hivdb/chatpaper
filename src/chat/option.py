# from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.shortcuts import input_dialog


from src.exceptions import check_selection
from src.preset import MODEL_RATE_LIMITS
from src.preset import DEFAULT_OPTIONS

from src.select_content.question import select_question
from src.select_content.question import select_question_set
from src.select_content.prompt_template import select_question_template
from src.select_content.llm_model import select_model
from src.select_content.paper import select_paper_content
from src.select_content.test_set import select_test_set
from src.select_content.prompt_template import load_prompt_template

from .chat_mode.one_q_all_content import one_q_all_content
from .chat_mode.multi_q_all_content import multi_q_all_content
from .chat_mode.one_q_embedding import one_q_embedding
from src.apis.embedding import get_token_length

from dataclasses import dataclass
from types import FunctionType


@dataclass
class ChatMode:
    model: str
    questions: dict
    papers: list
    question_template: str
    paper_template: str
    auto_mode_b: bool
    one_question_per_req_b: bool
    embedding_b: bool
    cheatsheet_b: bool
    cheatsheet: str
    chat_func: FunctionType
    chat_mode: str
    reserved_token: int
    req_token_limit: int


def select_chat_mode():
    # TODO: use default for some, model, question mode,
    # embedding mode, cheatsheet mode

    model = select_model()
    auto_mode = choose_auto_mode()
    test_set = select_test_set()

    if not auto_mode:
        papers = select_paper_content(test_set, only_one=True)
        questions = {}
        question_template = select_question_template(multi_questions=False)
        # TODO, queestion as a list
        question_mode = 'one_question_per_req'

        paper_template = load_prompt_template('paper_content')

        model_limit = MODEL_RATE_LIMITS[model]
        reserved_token = 300
        req_token_limit = model_limit['MAX_TOKENS'] - reserved_token

        return {
            # TODO, table or not
            # TODO, cheat sheet for embedding or not
            'model': model,
            'questions': questions,
            'papers': papers,
            'question_template': question_template,
            'paper_template': paper_template,
            'auto_mode?': auto_mode,
            'one_question_per_req?': True,
            'embedding?': False,
            'cheatsheet?': False,
            'cheatsheet': '',
            'chat_func': None,
            'chat_mode': 'manual chat',
            'reserved_token': reserved_token,
            'req_token_limit': req_token_limit,
        }

    papers = select_paper_content(test_set, all_option=True)

    question_set = select_question_set()
    questions = select_question(question_set, all_option=True)

    w_embedding = choose_embedding_mode()
    embedding_mode = 'embedding' if w_embedding else 'all_content'

    if w_embedding:
        question_mode = 'one_question_per_req'
        question_template = select_question_template(multi_questions=False)
        multi_question = False
    else:
        multi_question = choose_multi_ques_mode()
        question_mode = (
            'multi_questions'
            if multi_question
            else 'one_question_per_req')

        if not multi_question:
            question_template = select_question_template(multi_questions=False)
        else:
            question_template = select_question_template(multi_questions=True)

    w_cheatsheet = choose_cheatsheet_mode()
    cheatsheet = load_prompt_template('cheatsheet2')

    if (question_mode, embedding_mode) not in CHAT_MODE_LIST:
        raise Exception(f'{question_mode}, {embedding_mode} not supported')

    chat_func = CHAT_MODE_LIST[(question_mode, embedding_mode)]

    cheatsheet_mode = 'with_cheatsheet' if w_cheatsheet else 'wo_cheatsheet'

    paper_template = load_prompt_template('paper_content')

    model_limit = MODEL_RATE_LIMITS[model]
    reserved_token = 300 if not multi_question else 1000
    # TODO calc average answer token length
    # TODO how to estimate the reply length, reserve 1500 words for answer
    req_token_limit = model_limit['MAX_TOKENS'] - reserved_token

    if w_cheatsheet:
        req_token_limit -= get_token_length(cheatsheet)

    run_number = input_dialog(
        title='Please enter run number',
        text='Please enter run number:').run()
    if not run_number.isdigit():
        run_number = 1
    else:
        run_number = int(run_number)

    return {
        # TODO, table or not
        # TODO, cheat sheet for embedding or not
        'model': model,
        'questions': questions,
        'papers': papers,
        'question_template': question_template,
        'paper_template': paper_template,
        'auto_mode?': auto_mode,
        'one_question_per_req?': not multi_question,
        'embedding?': embedding_mode,
        'cheatsheet?': w_cheatsheet,
        'cheatsheet': cheatsheet,
        'chat_func': chat_func,
        'chat_mode': ', '.join([
            question_mode, embedding_mode, cheatsheet_mode]),
        'reserved_token': reserved_token,
        'req_token_limit': req_token_limit,
        'run_number': run_number,
    }


CHAT_MODE_LIST = {
    ('one_question_per_req', 'all_content'): one_q_all_content,
    ('multi_questions', 'all_content'): multi_q_all_content,
    ('one_question_per_req', 'embedding'): one_q_embedding,
    # 'one_q_all_content;map_reduce': {
    #     'desc': 'Map reduce mode',
    #     'func': chat_map_reduce,
    # },
    # TODO 'Refine mode'
}


@check_selection()
def choose_auto_mode(
        title="Auto or REPL mode", desc="Automatically chat the paper?"):

    if 'auto_mode' in DEFAULT_OPTIONS:
        return DEFAULT_OPTIONS['auto_mode']

    result = yes_no_dialog(
        title=title,
        text=desc,
        ).run()

    return result


@check_selection()
def choose_multi_ques_mode(
        title="Question mode", desc="Multiple questions per request?"):

    if 'multiple_questions?' in DEFAULT_OPTIONS:
        return DEFAULT_OPTIONS.get('multiple_questions?')

    result = yes_no_dialog(
        title=title,
        text=desc,
        ).run()

    return result


@check_selection()
def choose_embedding_mode(
        title="Using embedding method?",
        desc=""):

    if 'embedding?' in DEFAULT_OPTIONS:
        return DEFAULT_OPTIONS.get('embedding?')

    result = yes_no_dialog(
        title=title,
        text=title,
        ).run()

    return result


@check_selection()
def choose_cheatsheet_mode(
        title="Cheatsheet mode",
        desc="Using cheatsheet?"):

    if 'cheatsheet?' in DEFAULT_OPTIONS:
        return DEFAULT_OPTIONS.get('cheatsheet?')

    result = yes_no_dialog(
        title=title,
        text=desc,
        ).run()

    return result


# @check_selection()
# def choose_overwrite_result(title='Overwrite result?'):
#     default = False
#     result = radiolist_dialog(
#         title=title,
#         text='',
#         values=[
#             (True, 'Yes'),
#             (False, "No"),
#         ],
#         default=default
#         ).run()

#     return result
