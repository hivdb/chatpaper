from src.logs import logger
from src.doc_format.md import split_md_section
from ..map_reduce import try_map_reduce
from ..chat_history import ChatHistory
# from ..filter_question import get_unanswered


def multi_q_all_content(paper_file_path, chat_context, num_batch=20):

    # TODO, decorator
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

    while num_batch >= 1:
        batches = get_batches(chat_context['questions'], num_batch)
        try:
            try_batches(batches, chat_context)
            break
        except KeyError as e:
            print(repr(e))
            if num_batch <= 1:
                raise e
            num_batch = 1

    chat_history.dump_log()


def try_batches(batches, chat_context):
    for one_batch in batches:
        print(len(one_batch))

        try_map_reduce(dict(one_batch), chat_context)


def get_batches(questions, batch):

    batches = []

    questions = list(questions.items())

    num_batch = len(questions) // batch + (1 if len(questions) % batch else 0)

    for i in range(num_batch):
        one_batch = questions[i * batch: (i + 1) * batch]
        batches.append(dict(one_batch))

    return batches
