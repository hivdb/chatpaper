from src.doc_format.md import split_md_section
from src.logs import logger
from ..chat_history import ChatHistory
# from ..filter_question import get_unanswered
from ..map_reduce import try_map_reduce


def one_q_all_content(paper_file_path, chat_context):
    chat_history = ChatHistory(paper_file_path, chat_context)
    chat_context['chat_history'] = chat_history

    # questions = get_unanswered(
    #     chat_context['questions'],
    #     chat_history
    # )

    # if not questions:
    #     logger.info('Questions were answered.')
    #     return

    chat_context['doc_parts'] = split_md_section(paper_file_path)

    for qid, q in chat_context['questions'].items():
        logger.debug(f'Question: {q}')

        try_map_reduce({qid: q}, chat_context)

    chat_history.dump_log()
