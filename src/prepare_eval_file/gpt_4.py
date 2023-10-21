from src.file_format import load_csv
from src.file_format import dump_csv
from operator import itemgetter
from src.table import group_records_by

from .translate_answer.get_human_answer import get_human_answer
from .translate_answer.get_question_type import get_question_type
from .translate_answer.translate_AI_NA import translate_AI_NA
# from .translate_answer.translate_human_NA import translate_human_NA
from .translate_answer.translate_AI_reply import translate_AI_reply
from .translate_answer.get_AI_reply import get_AI_reply
# from .translate_answer.reduce_AI_reply import reduce_AI_reply

from src.evaluation.quick_eval import quick_eval
from src.evaluation.quick_eval import load_eval_db
from .shuffle import shuffle_by_paper


CHAT_MODE_MAP = {
    'all_content, wo_cheatsheet': 'base',
    'all_content, with_cheatsheet': 'guide',
    'embedding, wo_cheatsheet': 'embed',
    'embedding, with_cheatsheet': 'embed_guide',
}


def gen_eval_file(test_set_folder_list):
    # TODO, when to merge multiple paper data set?

    for t in test_set_folder_list:
        for i in range(1, 1000):
            gen_eval_file_for_testset(t, i)


def gen_eval_file_for_testset(test_set_folder, run_number):

    eval_db = load_eval_db(test_set_folder / 'evaluation' / 'eval_db.csv')

    eval_table = []

    for f, name in get_chat_history(test_set_folder / 'Papers'):
        report = load_csv(f)

        report = [
            i
            for i in report
            if int(i['run_number']) == run_number
        ]

        # chat_mode = set([
        #     i['chat_mode']
        #     for i in report
        # ])
        # if len(chat_mode) > 4:
        #     print(name, len(chat_mode), chat_mode)
        # if 'one_question_per_req, all_content, wo_cheatsheet' in chat_mode:
        #     print(name, 'oneoneone')

        report = get_paper_name(report, name)
        report = get_question_type(report)

        report = get_AI_reply(report)

        report = translate_AI_NA(report)
        report = translate_AI_reply(report)
        # report = reduce_AI_reply(report)

        human_answer_file = f.parent.parent / 'human_answer.csv'
        report = get_human_answer(report, human_answer_file)

        # report = translate_human_NA(report)

        [quick_eval(i, eval_db) for i in report]

        report = simplify_chat_mode(report)
        report = simplify_model(report)

        eval_table.extend(report)

    if not eval_table:
        return

    eval_table.sort(key=itemgetter(
        'model', 'chat_mode',
        'paper', 'question_id'))

    for key, table in group_records_by(
            eval_table, ['model', 'chat_mode']).items():

        key = dict(key)

        for i, j in group_records_by(table, ['paper']).items():
            if run_number >= 100:
                continue
            if len(j) != 60 and 'embed' not in key['chat_mode']:
                print(i, len(j), key['chat_mode'], run_number)

        if 'embed' in key['chat_mode']:
            continue

        if run_number == 1:
            file_name = f"{key['model']}_{key['chat_mode']}.csv"
        else:
            file_name = f"{key['model']}_{key['chat_mode']}_{run_number}.csv"

        gen_eval_file_by_model(
            test_set_folder / 'evaluation' / file_name,
            table)


def gen_eval_file_by_model(file_path, report):

    report.sort(key=lambda x: (x['paper'], int(x['question_id'])))

    dump_csv(
        file_path,
        report,
        headers=[
            'paper',
            'question_id',
            'question',
            'question_type',
            'human_answer',
            'human_NA',
            'AI_reply',
            'AI_NA',
            'AI_answer',
            'agree?',
            'explain',
            'correct_explain?',
            'sentences',
            'correct_sentences?',
            'confidence',
        ])

    return report


# TODO move to chat history folder
# TODO design a paper info model
def get_chat_history(folder):
    # TODO, check Paper folder format, check folder format function,
    # folder format definition

    for i in folder.iterdir():
        if not i.is_dir():
            continue

        history_folder = i / 'chat_history'
        if not history_folder.exists():
            # TODO give warning
            continue

        chat_history_file = history_folder / 'chat_history.csv'
        if not chat_history_file.exists():
            # TODO give warning
            continue

        yield chat_history_file, i.name


def get_paper_name(report, paper_name):

    for c in report:
        c['paper'] = paper_name

    return report


def simplify_chat_mode(report):

    [
        i.update({
            'chat_mode':
                ', '.join([j.strip() for j in i['chat_mode'].split(',')[1:]])
        })
        for i in report
    ]

    [
        i.update({
            'chat_mode': CHAT_MODE_MAP[i['chat_mode']]
        })
        for i in report
    ]

    return report


def simplify_model(report):
    [
        i.update({
            'model': '-'.join(i['model'].split('-')[:2])
        })
        for i in report
    ]

    return report
