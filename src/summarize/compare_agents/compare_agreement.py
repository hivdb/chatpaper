import pandas as pd


def compare_agreement(save_path, data_file_list):

    df_list = [
        convert_yes_to_number(pd.read_csv(i))
        for i in data_file_list
    ]

    df_list = [
        i.rename(
            columns={'agree?': j.stem})
        for i, j in zip(df_list, data_file_list)
    ]

    df = df_list[0]

    for i in df_list[1:]:
        df = df.merge(i, on=[
            'paper', 'question_id', 'question', 'question_type'], how='inner')

    columns = df.columns.tolist()
    columns.remove('paper')
    columns.remove('question_id')
    columns.remove('question')
    columns.remove('question_type')
    df['# agree'] = df[columns].sum(axis=1)

    df.to_csv(save_path, index=False)


def convert_yes_to_number(df):
    WANTED_COLUMNS = [
        'paper',
        'question_id',
        'question',
        'question_type',
        "agree?",
    ]

    df = df[WANTED_COLUMNS]
    df = df.copy()

    df['agree?'] = df['agree?'].str.lower()
    df['agree?'] = df['agree?'].str.strip()
    df['agree?'] = df['agree?'].str.rstrip('?')
    df['agree?'] = df['agree?'].map({
        'yes': 1, 'no': 0, 'yes, partial': 1})

    return df
