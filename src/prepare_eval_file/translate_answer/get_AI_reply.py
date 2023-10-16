def get_AI_reply(report):
    [
        i.update({'AI_reply': i['answer']})
        for i in report
    ]

    for i in report:
        del i['answer']

    return report
