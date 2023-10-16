NA_KEYWORDS = [
    'not mention',
    'not mentioned',
    'no mention',
    'no indication',
    'not report',
    'not specify',
    'not specified',
    'not provide',
    'not explicitly mention',
    'not explicitly state',
    'not explicitly report',
    'not enough information',
    'not involve',
    'not available',
    'not applicable',
    'unable to determine',
    'cannot determine',
    'cannot be determined',
    'n/a',
    'unable to answer',
    'does not indicate',
    'not stated',
    'does not contain any information',
    'dose not state',
    'unable to answer',
    'unknown',
]


def translate_AI_NA(table):

    for i in table:
        # if ('AI_NA' in i) and (i['AI_NA'] != ''):
        #     continue

        reply = i['AI_reply'].lower().strip()

        is_NA = 'No'
        # TODO default is No

        if not reply:
            is_NA = 'Yes'

        for keyword in NA_KEYWORDS:
            if keyword in reply:
                is_NA = 'Yes'
                break

        if reply.startswith('yes,'):
            is_NA = 'No'
        elif reply.startswith('no,'):
            is_NA = 'No'

        i['AI_NA'] = is_NA

    # print(len([
    #     i
    #     for i in table
    #     if i['AI_NA'] == '']))

    return table
