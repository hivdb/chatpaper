from prompt_toolkit.shortcuts import radiolist_dialog
from src.exceptions import check_selection
from src.prepare_doc import batch_prepare_files
from src.chat import chat
from src.logs import logger
from src.summarize import summarize

from src.prepare_eval_file import prepare_eval_file
from src.prepare_eval_file import combine_chat_history
from src.prepare_eval_file.update_human_answer import update_human_answer
from src.prepare_eval_file import prepare_claude_eval_file

from src.cleanup import archive_folder, cleanup_folder  # noqa
from src.cleanup import cleanup_question  # noqa
from src.chat.chat_history import fix_chat_history_question  # noqa
from src.chat.chat_history import fix_chat_history_run_number  # noqa
from src.chat.chat_history import remove_chat_history_run_number_and_qid  # noqa
from src.chat.chat_history import remove_chat_history_run_number  # noqa
from src.prepare_eval_file.shuffle import shuffle_by_paper
from src.prepare_eval_file import analysis_cost
from src.collect_pdf import collect_pdf
from src.fine_tune.prepare_data import prepare_data
from src.fine_tune.get_data_distribution import get_data_distribution
from src.fine_tune.fine_tune_gpt4o import monitor_job, fine_tune_gpt4o
from src.fine_tune.test_fine_tune import test_fine_tune
from src.fine_tune.fine_tune_gpt4o import del_ft_job


MODES = {
    'Prepare papers': batch_prepare_files,
    'Chat AI': chat,
    # 'Update human answer': update_human_answer,
    'Combine chat history': combine_chat_history,
    # 'Prepare eval file': prepare_eval_file,
    # 'Prepare claude eval file': prepare_claude_eval_file,
    # 'Shuffle': shuffle_by_paper,
    # 'Summarize & Visualize': summarize,
    # 'Cost': analysis_cost,
    # 'Fix Chat history': fix_chat_history_question
    # 'Fix Chat history': fix_chat_history_run_number,
    # 'Fix Chat history': remove_chat_history_run_number,
    # 'Fix chat history': remove_chat_history_run_number_and_qid,
    'Clean up folder': cleanup_folder,
    'Collect PDF': collect_pdf,
    'Prepare fine tuning': prepare_data,
    'Get data distribution': get_data_distribution,
    'Fine tune GPT4o': fine_tune_gpt4o,
    'Monitor fine tune GPT4o': monitor_job,
    'Delete fine tune GPT4o job': del_ft_job,
    'Test fine tuned model': test_fine_tune,
    # 'Archive folder': archive_folder,
    # 'Clean up question': cleanup_question,
}


@check_selection()
def select_run_mode(
        title='Please choose mode.', desc=''):
    mode_names = list(MODES.keys())
    default = mode_names[0]

    result = radiolist_dialog(
        title=title,
        text=desc,
        values=[
            (i, i)
            for i in mode_names
        ],
        default=default
        ).run()

    return result


def run_mode(mode_name):
    processor = MODES[mode_name]

    if not processor:
        logger.info(f"{mode_name} hasn't been supported yet.")
        return

    processor()
