from src.file_format import load_csv
from src.table import group_records_by
from collections import defaultdict


def load_eval_db(eval_db_path):
    eval_db = load_csv(eval_db_path)

    index = defaultdict(dict)

    for qid, q in group_records_by(eval_db, ['paper', 'question_id']).items():

        map = defaultdict(set)
        for i in q:
            reply = i['AI_reply']
            answer = i['AI_answer']
            map[reply].add(answer)

        for i, j in map.items():
            if len(j) != 1:
                print('Check eval db consistency', qid, len(j))

        map = defaultdict(set)
        for i in q:
            reply = i['AI_reply']
            agree = i['agree?']
            map[reply].add(agree)

        for i, j in map.items():
            if len(j) != 1:
                print('Check eval db consistency', qid, len(j))

        key = dict(qid)
        index[key['question_id']][key['paper']] = defaultdict(dict)

        for i in q:
            reply = i['AI_reply']
            answer = i['AI_answer']
            agree = i['agree?']
            index[key['question_id']][key['paper']][reply] = (answer, agree)

    return index


def quick_eval(record, eval_db):

    result = ''

    human_answer = record['human_answer'].lower().strip()
    # human_NA = record['human_NA'].lower().strip() == 'yes'
    ai_answer = record['AI_answer'].lower().strip()
    ai_reply = record['AI_reply'].lower().strip()
    # ai_NA = record['AI_NA'].lower().strip() == 'yes'

    index_result = eval_db[record['question_id']][record['paper']][ai_reply]

    if index_result:
        record['AI_answer'] = index_result[0]
        record['agree?'] = index_result[1]
        return

    if human_answer == ai_reply:
        result = 'Yes'
    elif human_answer == ai_answer:
        result = 'Yes'
    # elif human_NA and ai_NA:
    #     result = 'Yes'
    elif record['question_type'] == 'Boolean':
        result = quick_eval_boolean(
            # human_answer, human_NA, ai_answer, ai_reply, ai_NA)
            human_answer, ai_answer, ai_reply)
    elif record['question_type'] == 'Numerical':
        result = quick_eval_numerical(
            human_answer, ai_answer, ai_reply)
    elif record['question_type'] == 'Categorical':
        result = quick_eval_categorical(
            human_answer, ai_answer, ai_reply)

    record['agree?'] = result


def quick_eval_boolean(human_answer, ai_answer, ai_NA):

    if human_answer.startswith('yes') and ai_answer.startswith('yes'):
        return 'Yes'
    elif human_answer.startswith('no') and ai_answer.startswith('no'):
        return 'Yes'

    elif human_answer.startswith('yes') and ai_answer.startswith('no'):
        return 'No'
    elif human_answer.startswith('no') and ai_answer.startswith('yes'):
        return 'No'

    elif human_answer.startswith('yes') and ai_NA:
        return 'No'
    elif human_answer.startswith('no') and human_answer != 'no' and ai_NA:
        return 'No'
    elif human_answer.startswith('no') and ai_NA:
        return 'Yes'

    return ''


def quick_eval_categorical(human_answer, ai_answer, ai_reply):

    if human_answer in ai_reply:
        return 'Yes'

    if human_answer in ai_answer:
        return 'Yes'

    # if not human_NA and ai_NA:
    #     return 'No'

    return ''


def quick_eval_numerical(human_answer, ai_answer, ai_reply):

    human_answer = human_answer.split(',')[0].strip()

    if not human_answer.isdigit():
        return ''

    if not ai_answer.isdigit():
        return ''

    human_answer = int(human_answer)
    ai_answer = int(ai_answer)
    if human_answer == 0 and ai_answer == 0:
        return 'Yes'
    if human_answer != 0 and ai_answer == 0:
        return 'No'
    if human_answer == 0 and ai_answer != 0:
        return 'No'
    if human_answer != ai_answer:
        return 'No'

    return ''
