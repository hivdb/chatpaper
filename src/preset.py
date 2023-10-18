from pathlib import Path

WS = Path(__file__).resolve().parent.parent

# TODO: path as a file module, yaml file

ENV_PATH = WS / '.env'
PROMPT_TEMPLATE_PATH = WS / 'prompt_template'
PAPER_PATH = WS / 'papers'
QUESTION_PATH = WS / 'questions'
RATE_LIMIT_PATH = WS / '.rate_limit.json'

# TODO, yaml or toml file
MODEL_RATE_LIMITS = {
    # 'gpt-3.5-turbo': {
    #     'RPM': 3500,
    #     'TPM': 90000,
    #     'MAX_TOKENS': 4096,
    #     'type': 'chat-model',
    # },
    'gpt-3.5-turbo-16k': {
        'RPM': 3000,
        'TPM': 250000,
        'MAX_TOKENS': 16384,
        'type': 'chat-model',
    },
    'gpt-4': {
        'RPM': 3000,
        'TPM': 40000,
        'MAX_TOKENS': 8192,
        'type': 'chat-model',
    },
    'gpt-4-0314': {
        'RPM': 3000,
        'TPM': 40000,
        'MAX_TOKENS': 8192,
        'type': 'chat-model',
    },
    'gpt-4-32k': {
        'RPM': 200,
        'TPM': 40000,
        'MAX_TOKENS': 32768,
        'type': 'chat-model',
    },
    # 'gpt-4-32k-0613': {
    #     'RPM': 200,
    #     'TPM': 40000,
    #     'MAX_TOKENS': 32768,
    #     'type': 'chat-model',
    # },
    'text-embedding-ada-002': {
        'RPM': 3000,
        'TPM': 2500000,
        'type': 'embedding-model',
    },
}


DEFAULT_OPTIONS = {
    'model': 'gpt-4-32k',
    'auto_mode': True,
    'papers': 'all',
    'file_format': 'checked.md',
    # 'question_set': 'Set1',
    'questions': 'all',
    'embedding?': False,
    'multiple_questions?': True,
    # 'cheatsheet?': False,
}
