from prompt_toolkit.shortcuts import input_dialog
from prompt_toolkit.shortcuts import message_dialog
from src.logs import logger
from prompt_toolkit.shortcuts import yes_no_dialog
from copy import deepcopy


def chat_repl(chat_context, chat_func):

    paper = chat_context['papers'][0]

    qid = 1000  # manual question

    while True:
        question = get_question()

        if (question.lower().strip() in ('quit', '')):
            break

        qid += 1
        chat_context['questions'] = {qid: question}

        logger.info('Finding the answer....')

        answer = chat_func(paper, deepcopy(chat_context))

        show_answer(answer)

        _continue = yes_no_dialog(
            title='Continue?',
            text='').run()

        if not _continue:
            break


def get_question(cmd=True):
    if cmd:
        question = input('\nPlease enter your question: ')
    else:
        question = input_dialog(
            title='Please enter your question',
            text='',
            default=''
            ).run()

    return question


def show_answer(answer, cmd=True):
    if cmd:
        print(f"Answer:\n{answer}")
    else:
        message_dialog(
            title='Answer',
            text=answer).run()
