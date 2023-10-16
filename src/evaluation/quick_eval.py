

def quick_eval(record):

    result = ''

    human_answer = record['human_answer'].lower().strip()
    human_NA = record['human_NA'].lower().strip() == 'yes'
    ai_answer = record['AI_answer'].lower().strip()
    ai_reply = record['AI_reply'].lower().strip()
    ai_NA = record['AI_NA'].lower().strip() == 'yes'

    if human_answer == ai_reply:
        result = 'Yes'
    elif human_answer == ai_answer:
        result = 'Yes'
    elif human_NA and ai_NA:
        result = 'Yes'
    elif record['question_type'] == 'Boolean':
        result = quick_eval_boolean(
            human_answer, human_NA, ai_answer, ai_reply, ai_NA)
    elif record['question_type'] == 'Numerical':
        result = quick_eval_numerical(
            human_answer, human_NA, ai_answer, ai_reply, ai_NA)
    elif record['question_type'] == 'Categorical':
        result = quick_eval_categorical(
            human_answer, human_NA, ai_answer, ai_reply, ai_NA)

    record['agree?'] = result


def quick_eval_boolean(human_answer, human_NA, ai_answer, ai_reply, ai_NA):

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


def quick_eval_categorical(human_answer, human_NA, ai_answer, ai_reply, ai_NA):

    if human_answer in ai_reply:
        return 'Yes'

    if human_answer in ai_answer:
        return 'Yes'

    if not human_NA and ai_NA:
        return 'No'

    return ''


def quick_eval_numerical(human_answer, human_NA, ai_answer, ai_reply, ai_NA):

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
