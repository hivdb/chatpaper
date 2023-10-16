from src.select_content.test_set import select_test_set
from prompt_toolkit.shortcuts import radiolist_dialog
from src.exceptions import check_selection
from src.table import group_records_by
from src.file_format import load_csv
from src.file_format import dump_csv
from src.excel2csv import excel2csv


def list_check_list(path):
    # TODO only use GPT-4 excel file

    result = []
    for i in (path / 'evaluation').iterdir():
        if i.suffix != '.csv':
            continue
        result.append((i, i.name))

    return result


@check_selection()
def choose_checked_answer(
        path, title='Please select the file with updated human answer'):
    check_file_list = list_check_list(path)

    result = radiolist_dialog(
        title=title,
        text='',
        values=check_file_list,
    ).run()

    return result


def update_human_answer():

    test_set_path = select_test_set()

    # file_path = choose_checked_answer(test_set_path)
    excel_file = test_set_path / 'evaluation' / 'gpt-4_base.xlsx'
    excel2csv(excel_file, excel_file.stem)
    content = load_csv(test_set_path / 'evaluation' / 'gpt-4_base.csv')

    paper_info = group_records_by(content, 'paper')

    for i in (test_set_path / 'Papers').iterdir():
        if not i.is_dir():
            continue

        paper_name = i.name
        result = [
            {
                'id': i['question_id'],
                'question': i['question'],
                'answer': i['human_answer'],
                'NA': i['human_NA'],
            }
            for i in paper_info[paper_name]
        ]
        dump_csv(i / 'human_answer.csv', result)
