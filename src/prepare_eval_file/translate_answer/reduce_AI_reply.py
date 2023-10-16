from src.table import group_records_by


# Only used for papers that was splited to several parts in query.
def reduce_AI_reply(report):
    for i in report:
        if not i['md5']:
            print(i)

    report = [
        i
        for i in report
        if i['md5']
    ]

    result = []
    for _, reply_list in group_records_by(
            report, ['model', 'chat_mode', 'question_id']).items():

        result.extend(reduce_one_question(reply_list))

    return result


def reduce_one_question(reply_list):

    reply_list = get_non_dup_reply(reply_list)
    if len(reply_list) == 1:
        return reply_list

    reply_list = get_non_NA_reply(reply_list)
    if len(reply_list) == 1:
        return reply_list

    reply_list = get_yes_reply(reply_list)
    if len(reply_list) == 1:
        return reply_list

    reply_list = get_no_reply(reply_list)
    if len(reply_list) == 1:
        return reply_list

    reply_list = get_more_detailed_reply(reply_list)

    return reply_list


def get_non_dup_reply(reply_list):

    results = []

    for _, same_reply in group_records_by(reply_list, 'AI_reply').items():
        results.append(same_reply[0])

    return results


def get_non_NA_reply(reply_list):

    non_NA_list = [
        i
        for i in reply_list
        if i['AI_NA'] != 'Yes'
    ]

    if not non_NA_list:
        return reply_list[:1]
    else:
        return non_NA_list


def get_yes_reply(reply_list):
    yes_list = [
        i
        for i in reply_list
        if i['AI_answer'] == 'Yes'
    ]

    if yes_list:
        yes_list.sort(key=lambda x: len(x['AI_reply']), reverse=True)
        return yes_list[:1]
    else:
        return reply_list


def get_no_reply(reply_list):
    no_list = [
        i
        for i in reply_list
        if i['AI_answer'] == 'No'
    ]

    if no_list:
        no_list.sort(key=lambda x: len(x['AI_reply']), reverse=True)
        return no_list[:1]
    else:
        return reply_list


def get_more_detailed_reply(reply_list):

    reply_list = [
        i
        for idx, i in enumerate(reply_list)
        if not any([
            is_sub_content(i['AI_reply'].strip(), j['AI_reply'].strip())
            for jdx, j in enumerate(reply_list)
            if idx != jdx])
    ]

    return reply_list


def is_sub_content(str1, str2):
    if str1 in str2:
        return True

    if all([i in str2.split() for i in str1.split()]):
        return True

    return False
