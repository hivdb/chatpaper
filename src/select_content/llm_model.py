from prompt_toolkit.shortcuts import radiolist_dialog
from src.preset import MODEL_RATE_LIMITS
from src.exceptions import check_selection
from src.preset import DEFAULT_OPTIONS


@check_selection()
def select_model(
        title="Please choose the LLM model",
        desc="",
        default='gpt-3.5-turbo'):

    if 'model' in DEFAULT_OPTIONS:
        return DEFAULT_OPTIONS['model']

    result = radiolist_dialog(
        title=title,
        text=desc,
        values=[
            (i, i)
            for i in list_model()
        ],
        default=default
    ).run()

    return result


def list_model():
    models = [
        name
        for name, config in MODEL_RATE_LIMITS.items()
        if config['type'] == 'chat-model'
    ]

    return models
