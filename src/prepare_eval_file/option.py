from prompt_toolkit.shortcuts import radiolist_dialog
from src.exceptions import check_selection


def list_report_date(folder):

    report_date_list = set()

    folder = folder / 'Papers'

    for i in folder.iterdir():
        if not i.is_dir():
            continue
        history_folder = i / 'chat_history'
        if not history_folder.exists():
            continue

        for j in history_folder.iterdir():
            if j.suffix == '.csv':
                date = j.stem.replace('chat_history_', '')
                report_date_list.add(date)

    report_date_list = sorted(list(report_date_list))

    return [
        (i, i)
        for i in report_date_list
    ]


# @check_selection()
# def select_report_date(
#         test_set_folder, title="Please select report date"):

#     report_date_list = list_report_date(test_set_folder)

#     result = radiolist_dialog(
#         title=title,
#         text='',
#         values=report_date_list,
#     ).run()

#     return result
