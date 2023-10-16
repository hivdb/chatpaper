from src.file_format import load_csv
from src.file_format import dump_csv
from ..by_question import seperate_questions
from .by_boolean import by_boolean
from .by_numerical import by_numerical
from .by_categorical import by_categorical


def summarize_ground_truth(data_file):
    table = load_csv(data_file)

    questions = seperate_questions(table)

    report_table = []
    report_table.extend(by_boolean(questions['boolean']))
    report_table.extend(by_numerical(questions['numerical']))
    report_table.extend(by_categorical(questions['categorical']))

    dump_csv(
        data_file.parent / 'summarize_ground_truth.csv',
        report_table)
