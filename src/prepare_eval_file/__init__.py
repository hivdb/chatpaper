from src.select_content.test_set import select_test_set
from .gpt_4 import gen_eval_file
from .claude import gen_claude_eval_file
from .ground_truth import get_ground_truth
from .cost import process_cost
from src.file_format import load_csv, dump_csv


def prepare_eval_file():

    test_set_path_list = select_test_set(dialog='check_list')

    get_ground_truth(test_set_path_list[0])

    gen_eval_file(test_set_path_list)


def prepare_claude_eval_file():
    test_set_path_list = select_test_set()

    # TODO: support multiple test set
    gen_claude_eval_file(test_set_path_list)


def analysis_cost():
    test_set = select_test_set()

    process_cost(test_set)


def combine_chat_history():

    test_set_path_list = select_test_set(dialog='check_list')

    result = []
    for f in test_set_path_list[0].iterdir():
        if not f.is_dir():
            continue

        chat_hist_file = f / 'chat_history' / 'chat_history.csv'

        if not chat_hist_file.exists():
            continue

        content = load_csv(chat_hist_file)
        [
            c.update({'PMID': f.name})
            for c in content
        ]
        result.extend(content)

    dump_csv(test_set_path_list[0] / 'chat_history.csv', result)
