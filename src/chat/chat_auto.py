from src.logs import logger
from copy import deepcopy


def chat_auto(chat_context, chat_func):

    papers = chat_context['papers']
    del chat_context['papers']

    for paper in papers:
        logger.info(f'Processing.... {paper.name}')

        chat_func(paper, deepcopy(chat_context))
