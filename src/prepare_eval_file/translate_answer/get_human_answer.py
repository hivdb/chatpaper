from src.file_format import load_csv


def get_human_answer(report, human_answer_file):

    human_answer = {
        str(i['id']): i['answer']
        for i in load_csv(human_answer_file)
    }

    human_na = {
        str(i['id']): i['NA']
        for i in load_csv(human_answer_file)
    }

    for r in report:
        r['human_answer'] = human_answer.get(str(r['question_id']), '')
        r['human_NA'] = human_na.get(str(r['question_id']), '')

    return report
