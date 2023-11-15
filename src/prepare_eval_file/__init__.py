from src.select_content.test_set import select_test_set
from .gpt_4 import gen_eval_file
from .claude import gen_claude_eval_file
from .ground_truth import get_ground_truth
from .cost import process_cost


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
