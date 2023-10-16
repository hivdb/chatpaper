from src.select_content.test_set import select_test_set
from src.select_content.paper import select_paper
from datetime import datetime
import shutil
from src.file_format import load_csv
from src.file_format import dump_csv


def cleanup_folder():

    test_set = select_test_set()

    papers = select_paper(test_set, all_option=True)

    today = datetime.today()
    date = today.strftime("%Y%m%d")

    for i in papers:
        chat_hist_path = i / 'chat_history'
        if not chat_hist_path.exists():
            continue
        shutil.move(chat_hist_path, i / 'archive' / date)


def cleanup_question():
    test_set = select_test_set()

    papers = select_paper(test_set, all_option=True)

    question_id = input('Please enter question id to remove: ')

    for i in papers:
        chat_hist_path = i / 'chat_history' / 'chat_history.csv'

        records = load_csv(chat_hist_path)

        records = [
            i
            for i in records
            if i['question_id'] != question_id
        ]

        dump_csv(chat_hist_path, records)
