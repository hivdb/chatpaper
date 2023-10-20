from prompt_toolkit.shortcuts import radiolist_dialog
from ..preset import PROMPT_TEMPLATE_PATH
from src.exceptions import check_selection


def select_question_template(multi_questions):
    prompt_template_path = select_one_prompt_template(
        multi_questions=multi_questions)

    with open(prompt_template_path) as fd:
        return fd.read()


RESEREVED_TEMPLATE = (
    'system',
    'cheatsheet',
    'paper_content',
    'simple',
    'auto_eval_answer',
)


def list_prompt_template(multi_questions, folder=PROMPT_TEMPLATE_PATH):
    templates = []
    for i in folder.iterdir():
        if not i.suffix.lower() == '.txt':
            continue

        if i.name.startswith('_'):
            continue

        if i.stem.lower() in RESEREVED_TEMPLATE:
            continue

        if multi_questions != ('multi_questions' in i.name):
            continue

        templates.append((i, i.stem.replace('_', ' ').capitalize()))

    return templates


@check_selection()
def select_one_prompt_template(
        title="Please choose the prompt template.",
        desc="",
        multi_questions=True):
    default = list_prompt_template(multi_questions)[0][0]

    if len(list_prompt_template(multi_questions)) == 1:
        return default

    result = radiolist_dialog(
        title=title,
        text=desc,
        values=list_prompt_template(multi_questions),
        default=default
        ).run()

    return result


def load_prompt_template(template_name, folder=PROMPT_TEMPLATE_PATH):
    for i in folder.iterdir():
        if template_name in i.name:
            with open(i) as fd:
                return fd.read()
