from src.file_format import load_csv
from src.file_format import dump_csv
from src.table import group_records_by


def get_ground_truth(test_set_folder):

    table = []
    for f in (test_set_folder / 'Papers').iterdir():
        if not f.is_dir():
            continue

        human_answer_file = f / 'human_answer.csv'
        human_answer = load_csv(human_answer_file)
        [
            i.update({'paper': f.name})
            for i in human_answer
        ]

        table.extend(human_answer)

    report = []
    for qid, q_list in group_records_by(table, 'id').items():
        row = {
            'id': qid,
            'question': q_list[0]['question']
        }
        for i in q_list:
            row[i['paper']] = i['answer']

        report.append(row)

    dump_csv(test_set_folder / 'evaluation' / 'human_answer.csv', report)
