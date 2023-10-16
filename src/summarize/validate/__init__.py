# TODO validate file headers
from .check_human_answer import check_human_answer
from .check_human_boolean_eval import check_human_boolean_eval
from .check_NA import check_NA


def validate(data_file_list):

    for f in data_file_list:

        if 'embed' in f.name:
            continue

        if 'old' in f.name:
            continue

        check_human_answer(f)

        check_human_boolean_eval(f)

        check_NA(f)
