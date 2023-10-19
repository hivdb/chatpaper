from src.file_format import load_csv
from src.table import group_records_by


def check_human_answer(f):

    paper_main_path = f.parent.parent / 'Papers'
    table = load_csv(f)

    for i in table:
        paper = i['paper']

        paper_path = paper_main_path / paper
        human_answer = get_human_answers(paper_path / 'human_answer.csv')
        # human_na = get_human_NA(paper_path / 'human_answer.csv')

        if i['human_answer'] != human_answer[i['question_id']]:
            print(
                f'Error: human answer changed, '
                f'{f} {paper}, {i["question_id"]}')

        # if i['human_NA'] != human_na[i['question_id']]:
        #     print(
        #         f'Error: human NA changed, '
        #         f'{f} {paper}, {i["question_id"]}')

    qids = human_answer.keys()

    for paper, q_list in group_records_by(table, ['paper']).items():
        paper_qids = [
            i['question_id']
            for i in q_list
        ]
        for i in qids:
            if i not in paper_qids:
                pass
                # print(f'Error: missing question {f}, {paper}, {i}')


def get_human_answers(human_answer_file):
    human_ans = {
        str(i['id']): i['answer']
        for i in load_csv(human_answer_file)
    }

    return human_ans


def get_human_NA(human_answer_file):
    human_ans = {
        str(i['id']): i['NA']
        for i in load_csv(human_answer_file)
    }

    return human_ans
