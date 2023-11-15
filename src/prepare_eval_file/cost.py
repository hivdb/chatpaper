from .gpt_4 import get_chat_history
from src.file_format import load_csv
from src.file_format import dump_csv
from src.table import group_records_by
from operator import itemgetter


def process_cost(test_set, run_number=[1, 2, 3, 4, 10, 11, 12, 15]):
    # TODO, when to merge multiple paper data set?

    reports = []
    for f, paper in get_chat_history(test_set / 'Papers'):
        table = load_csv(f)
        [
            i.update({'paper': paper})
            for i in table
        ]

        table = [
            i
            for i in table
            if int(i['run_number']) in run_number
            and 'embedding' not in i['chat_mode']
        ]

        reports.extend(table)

    gen_report(test_set / 'evaluation' / 'cost.csv', reports)


def gen_report(save_path, table):

    report = []
    for key, list in group_records_by(
            table, [
                'paper', 'chat_mode', 'run_number', 'date',
                'total_tokens', 'prompt_tokens', 'completion_tokens']).items():

        value = dict(key)

        value.update({
            'num_records': len(list)
        })

        report.append(value)

    report.sort(key=itemgetter('paper', 'chat_mode', 'run_number', 'date'))

    dump_csv(save_path, report, headers=[
        'paper', 'chat_mode', 'run_number', 'date',
        'total_tokens', 'prompt_tokens', 'completion_tokens', 'num_records'])
