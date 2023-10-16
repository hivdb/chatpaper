def get_unanswered(questions, part, chat_history, run_number):
    return {
        qid: q
        for qid, q in questions.items()
        if not chat_history.check_answer_exist(qid, q, part, run_number)
    }
