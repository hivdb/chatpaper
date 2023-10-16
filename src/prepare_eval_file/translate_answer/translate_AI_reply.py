from src.summarize.by_question import seperate_questions


def translate_AI_reply(table):

    questions = seperate_questions(table)

    by_boolean(questions['boolean'])
    by_numerical(questions['numerical'])
    by_categorical(questions['categorical'])

    return table


def by_boolean(questions):

    for i in questions:
        reply = i['AI_reply'].lower()
        question_type = i['question_type']

        ai_answer = ''

        if reply.startswith('yes'):
            ai_answer = 'Yes'
        elif reply == 'no' or reply.startswith('no,') or reply.startswith('no.'):
            ai_answer = 'No'

        elif i['AI_NA'] == 'Yes':
            ai_answer = 'NA'

        i['AI_answer'] = ai_answer


def by_numerical(questions):

    for i in questions:
        reply = i['AI_reply'].lower()
        question_type = i['question_type']

        ai_answer = ''

        if i['AI_NA'] == 'Yes':
            ai_answer = '0'
        elif reply.startswith('none'):
            ai_answer = '0'
        else:
            ai_ans = reply.split()[0]
            if ai_ans.isdigit():
                ai_answer = ai_ans

        i['AI_answer'] = ai_answer


def by_categorical(questions):

    for i in questions:
        reply = i['AI_reply'].lower()
        question_type = i['question_type']

        ai_answer = ''

        if i['AI_NA'] == 'Yes':
            ai_answer = 'NA'

        i['AI_answer'] = ai_answer
