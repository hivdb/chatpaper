from prompt_toolkit.shortcuts import radiolist_dialog
from ..preset import RAG_PATH
from src.exceptions import check_selection


def select_instruction():
    instruction_path = select_one_instruction()

    with open(instruction_path) as fd:
        return fd.read()


def list_instruction(folder=RAG_PATH):
    instructions = []
    for i in folder.iterdir():
        if not i.suffix.lower() == '.txt':
            continue

        if i.name.startswith('_'):
            continue

        instructions.append((i, i.stem.replace('_', ' ').capitalize()))

    return instructions


@check_selection()
def select_one_instruction(
        title="Please choose the RAG content.",
        desc=""):

    result = radiolist_dialog(
        title=title,
        text=desc,
        values=list_instruction(),
        ).run()

    return result


def load_instruction(instruction_name, folder=RAG_PATH):
    for i in folder.iterdir():
        if instruction_name in i.name:
            with open(i) as fd:
                return fd.read()
