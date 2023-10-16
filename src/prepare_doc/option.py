from prompt_toolkit.shortcuts import yes_no_dialog
from src.exceptions import check_selection


@check_selection()
def choose_overwrite(
        title="Overwrite prepared files?"):
    result = yes_no_dialog(
        title=title,
        text=title,
        ).run()

    return result


@check_selection()
def choose_generate_embedding(
        title="Generate embedding?"):
    result = yes_no_dialog(
        title=title,
        text=title,
        ).run()

    return result
