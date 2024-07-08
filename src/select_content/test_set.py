from src.preset import PAPER_PATH
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.shortcuts import checkboxlist_dialog
from src.exceptions import check_selection


def load_test_set(folder=PAPER_PATH):

    test_sets = []
    for i in folder.iterdir():
        if not i.is_dir():
            continue
        if 'set' in i.name.lower():
            test_sets.append((i, i.name))
        if i.name.lower().startswith('paper'):
            test_sets.append((i, i.name))

    test_sets.sort(key=lambda x: x[-1])

    return test_sets


@check_selection()
def select_test_set(title="Please select test set", dialog='radio'):

    if dialog == 'radio':
        dialog = radiolist_dialog
    else:
        dialog = checkboxlist_dialog

    test_sets = load_test_set()

    result = dialog(
        title=title,
        text='',
        values=test_sets,
    ).run()

    return result
