from src.apis.embedding import get_vectordb
from src.logs import logger
from ..chat_history import ChatHistory
# from ..filter_question import get_unanswered
from ..map_reduce import try_map_reduce


def one_q_embedding(paper_file_path, chat_context):
    chat_history = ChatHistory(paper_file_path, chat_context)
    chat_context['chat_history'] = chat_history

    # questions = get_unanswered(
    #     chat_context['questions'], chat_history)

    # if not questions:
    #     logger.info('Questions were answered.')
    #     return

    db = get_vectordb(paper_file_path, paper_file_path.parent, 'section')

    # TODO: dump search result, prevent rerun.

    for qid, q in chat_context['questions'].items():
        logger.debug(q)

        try:
            docs = db.similarity_search(q)
        except RuntimeError as e:
            if 'contigious' not in str(e):
                raise e
            db = get_vectordb(
                paper_file_path, paper_file_path.parent, 'paragraph')
            docs = db.similarity_search(q)

        chat_context['doc_parts'] = [
            {
                'all_content': i.page_content
            }
            for i in docs
        ]

        try_map_reduce({qid: q}, chat_context)

        # TODO, log embedding parts number

    chat_history.dump_log()
