def translate_human_NA(table):

    for j in table:
        j['human_NA'] = (
            'Yes'
            if is_NA(j['human_answer'])
            else 'No'
        )

    return table


def is_NA(human_answer):

    human_answer = human_answer.lower()

    if human_answer.startswith('na'):
        return True

    if 'not mentioned' in human_answer:
        return True

    if 'not applicable' in human_answer:
        return True

    if 'not available' in human_answer:
        return True

    return False
