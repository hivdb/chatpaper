from .option import select_chat_mode
from .chat_auto import chat_auto
from .chat_repl import chat_repl
from src.logs import logger


def chat():
    chat_context = select_chat_mode()
    logger.debug(chat_context)

    chat_func = chat_context['chat_func']
    del chat_context['chat_func']

    # print(chat_context['chat_mode'])
    if not chat_context['auto_mode?']:
        chat_repl(chat_context, chat_func)
    else:
        chat_auto(chat_context, chat_func)
